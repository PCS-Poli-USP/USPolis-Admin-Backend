# Logging

How request logging works: the two loggers set up in `server/logger.py`, what
`LoggerMiddleware` writes to each, and how file rotation is configured.

## Two separate loggers

`server/logger.py` defines two independent `logging.Logger` instances, each
writing to its own rotating file under `logs/`:

- `app_logger` (`logs/api.log`) — general request/response logging plus
  anything else the app logs via `from server.logger import logger`.
- `loki_access` (`logs/loki-access-api.log`) — a dedicated access log that
  Grafana Alloy ships into Grafana Loki. It has `propagate = False` so its
  records never also end up in `app_logger`'s handlers.

Neither logger calls Loki's HTTP API directly — both just write structured
lines to a local file. Shipping is external to this app: the `analytics`
Compose profile in the `USPolis-Admin` repo runs Loki, Alloy and Grafana
(see `analytics/README.md` there). Alloy reads `loki-access-api.log` from the
backend's log volume, read-only. Only that file is shipped: `api.log` keeps
query strings, and `/auth/refresh-token` carries a Google refresh token in
its URL.

Alloy parses the `loki_access` line with a regex in
`analytics/alloy/config.alloy`, so **changing the line format in
`server/logger.py` requires updating that regex** — a line that doesn't
match still reaches Loki, but with no labels or metadata extracted. Only
`method` and `status` are labels (low cardinality). `route` (the path with
ids replaced by `:id`), `path`, `client_ip`, `email` and `duration` are
structured metadata, filterable in LogQL without a parser:

```logql
{app="uspolis-backend-api", status=~"5.."} | route="/classrooms/full/:id"
```

This replaced a host install (Loki and Promtail binaries in a local,
non-git `../USPolis-Analytics` folder). Promtail reached end of life in
March 2026.

## What `LoggerMiddleware` writes

`LoggerMiddleware` in `server/middlewares/logger_middleware.py` wraps every request:

- It always logs a request entry and a response entry to `app_logger`
  (method, path, status, duration, user email, and — for certain
  method/path combinations listed in `LOG_BODY_RULES` — the request body).
- For a matched method/path, the captured body is also attached to the
  **response** log line whenever that response is an error
  (`status_code >= 400`), alongside `status` and `detail`. So a single
  `grep 'status="409"'` (or any other error status) surfaces the payload
  that caused it, not just a separate, harder-to-correlate request line.
  To make a new route's body show up this way, add its method/path to
  `LOG_BODY_RULES` in `server/middlewares/logger_middleware.py` — that one table drives both
  the request-line logging and the error-response-line logging.
- Before any body is logged or persisted, keys listed in
  `SENSITIVE_BODY_KEYS` are replaced with `***REDACTED***` at any depth
  (case-insensitive): `password` (the user's Júpiter password) and `token`
  (the secret of a one-time API key delivery link, posted to
  `/api-key-links/.../reveal` and to the admin share-link email route). Add
  a key there whenever a new request body carries a secret.
- After the response, unless the method is `OPTIONS` or the path starts with
  one of `LOKI_EXCLUDED_PATHS` (`/health`, `/analytics`, `/api/docs`,
  `/api/openapi.json`), it also emits one line to `loki_access`:

  ```
  [date] LEVEL client_ip="..." method="..." path="..." status="..." duration="..." email="..."
  ```

  `client_ip` comes from `get_client_ip()`, i.e. `request.client.host` —
  which Uvicorn resolves from `X-Forwarded-For` only for proxies listed in
  `--forwarded-allow-ips` (the raw header is never trusted; see
  `RATE_LIMIT.md`).
  `email` is the authenticated user's email, whichever way they
  authenticated: `request.state.user_info` (Bearer token) or, failing that,
  `request.state.current_user`, which every authenticator sets (session
  cookie, token, the `OVERRIDE_AUTH` mock). Anonymous requests get `"N/A"`.
  The same lookup fills the `user_email` of the `api.log` lines.
  `duration` is in milliseconds.

## Nothing is written on the request's path

A request never waits for a log write or for the database:

- **Log lines go through a bounded queue.** Each logger has a
  `DroppingQueueHandler`: the request only puts the record on a queue of
  `LOG_QUEUE_MAX_SIZE` records (default 10 000, per logger and worker), and a
  `QueueListener` thread writes it to the file. When the queue is full the
  record is **dropped** rather than blocking, and the next record that fits is
  followed by `WARNING Log queue full: N records dropped` (at most once a
  minute). The listener is stopped with `atexit`, which writes what is still
  queued, and restarted in a forked child (`os.register_at_fork`), since
  threads don't survive `fork`.
- **`apiaccesslog` rows are written in batches.** The middleware only queues
  the row (`ACCESS_LOG_WRITER.enqueue`, in
  `server/services/access_log_writer.py`). A task started by the app
  lifespan saves what accumulated in **one transaction**, in a thread, every
  `ACCESS_LOG_FLUSH_SECONDS` (2 s), or right away once
  `ACCESS_LOG_FLUSH_BATCH` (200) rows are waiting. On shutdown the task is
  cancelled and a final flush saves the rest. `timestamp` is when the
  response happened, not when the row was saved. A failed batch is logged
  and discarded (no retry, so rows don't pile up while the database is down).
- **Error floods are capped.** At most `ACCESS_LOG_MAX_PER_IP_PER_MINUTE` (30)
  error rows per client (IPv6 grouped by /64, as in the rate limiter) per
  minute are saved. The rest of that minute becomes **one** summary row,
  tagged `ErrorFlood`, copied from the last suppressed request, whose
  `detail` says how many were left out. It counts as one row in the
  status-code summary. At most `ACCESS_LOG_BUFFER_MAX` (5 000) rows wait to be
  saved; past it rows are dropped and
  `WARNING API access log buffer full: N rows dropped` is logged. The first
  429 per IP and window (see `RATE_LIMIT.md`) skips the per-client cap.
- **Bodies are only parsed when they will be used.** The request body is
  read once, raw, when the route matches `LOG_BODY_RULES` or the body is
  JSON/text. It is decoded and redacted only for a `LOG_BODY_RULES` log line
  or an `apiaccesslog` row that was actually kept. The response body is
  buffered only for a **JSON error** (status >= 400) to read its `message`.
  Any other response passes through untouched and still streams, so the
  `api.log` Response line of a 2xx has `response_detail="N/A"`. Bodies over
  `LOG_BODY_MAX_BYTES` (64 KB) are never buffered, parsed or logged.

## Rotation

Both loggers rotate by **file size**, not on a schedule, with
`LockedRotatingFileHandler` (in `server/logger.py`), a `RotatingFileHandler`
that is safe with several gunicorn workers on the same file. The stock
handler rotates per process: when one worker renames `api.log` to
`api.log.1`, the others keep writing to their old descriptor (now the `.1`)
and measure size with their own offset, so rotations repeat, `rename` fails
and lines are lost (about 9% of the lines with 4 processes in a local test).
Each write now takes an exclusive `flock` on `<file>.lock`, reopens the file
if another worker rotated it, decides from the real size on disk, and
rotates/writes before releasing. The waiting happens on the listener thread,
never on the event loop, and the kernel drops the lock if a worker dies.
Linux/Unix only (`fcntl`).

| Logger | File | `maxBytes` | `backupCount` |
|---|---|---|---|
| `app_logger` | `logs/api.log` | `LOG_MAX_SIZE` env var, default `1_073_741_824` (1 GB) | `LOG_BACKUP_COUNT` env var, default `2` |
| `loki_access` | `logs/loki-access-api.log` | `10485760` (10 MB, fixed) | `5` (fixed) |

When a write would push the current file past `maxBytes`, the handler closes
it, shifts existing backups up by one suffix (`.log.1` → `.log.2`, ...,
`.log` → `.log.1`, dropping anything past `backupCount`), and opens a fresh
empty file at the original name for the new record. `loki-access-api.log`
is not configurable via environment variables — its limits are hardcoded in
`server/logger.py`.
