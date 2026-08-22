# Logging

How request logging works: the two loggers set up in `server/logger.py`, what
`LoggerMiddleware` writes to each, and how file rotation is configured.

## Two separate loggers

`server/logger.py` defines two independent `logging.Logger` instances, each
writing to its own rotating file under `logs/`:

- `app_logger` (`logs/api.log`) — general request/response logging plus
  anything else the app logs via `from server.logger import logger`.
- `loki_access` (`logs/loki-access-api.log`) — a dedicated access log meant to
  be scraped/shipped (e.g. by Promtail/Grafana Agent) into Grafana Loki. It
  has `propagate = False` so its records never also end up in `app_logger`'s
  handlers.

Neither logger calls Loki's HTTP API directly — both just write structured
lines to a local file. Shipping those files into Loki is external to this
app (no shipping config lives in this repo).

## What `LoggerMiddleware` writes

`LoggerMiddleware` in `server/middlewares.py` wraps every request:

- It always logs a request entry and a response entry to `app_logger`
  (method, path, status, duration, user email, and — for certain
  method/path combinations listed in `LOG_BODY_RULES` — the request body).
- For a matched method/path, the captured body is also attached to the
  **response** log line whenever that response is an error
  (`status_code >= 400`), alongside `status` and `detail`. So a single
  `grep 'status="409"'` (or any other error status) surfaces the payload
  that caused it, not just a separate, harder-to-correlate request line.
  To make a new route's body show up this way, add its method/path to
  `LOG_BODY_RULES` in `server/middlewares.py` — that one table drives both
  the request-line logging and the error-response-line logging.
- After the response, unless the method is `OPTIONS` or the path starts with
  one of `LOKI_EXCLUDED_PATHS` (`/health`, `/analytics`, `/api/docs`,
  `/api/openapi.json`), it also emits one line to `loki_access`:

  ```
  [date] LEVEL client_ip="..." method="..." path="..." status="..." duration="..." email="..."
  ```

  `client_ip` comes from `get_client_ip()` — the first entry of the
  `X-Forwarded-For` header if present, otherwise `request.client.host`.
  `email` comes from `request.state.user_info` when the request is
  authenticated, otherwise `"N/A"`. `duration` is in milliseconds.

## Rotation

Both loggers use the standard library's `RotatingFileHandler`, which rotates
by **file size**, not on a schedule:

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
