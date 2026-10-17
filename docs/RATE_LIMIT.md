# Rate Limiting

How the API limits request rates per client IP: the two layers (Nginx and the
backend middleware), how the limits were chosen, how to configure and roll it
out, and how to run the Redis it depends on.

API keys for partners (per-key limits) build on top of this and are not
implemented yet.

## Two layers

1. **Nginx `limit_req` / `limit_conn`.** These run in C and cost almost
   nothing, so they reject floods before they reach Python. They are
   deliberately **looser** than the app limits (10 req/s with a burst of 40).
   Example config: `nginx/uspolis-api.conf.example` in the `USPolis-Admin`
   repo.
2. **`RateLimitMiddleware`** (`server/middlewares/rate_limit_middleware.py`). It applies precise
   per-IP fixed windows, with counters kept in Redis so all Gunicorn workers
   share them. It is a pure ASGI middleware that runs **before routing and
   authentication**. A rejected request therefore costs one Redis round trip
   and nothing else; in particular, no call to Google to validate a token.

Middleware order, from outermost to innermost, is
`LoggerMiddleware → CORSMiddleware → RateLimitMiddleware → routes`:
- A 429 still carries CORS headers. Without them, the browser would report a
  CORS error instead of the 429.
- A 429 is still written to `logs/api.log`. Only the **first** 429 per IP per
  window is persisted to `apiaccesslog`; saving every rejected request would
  mean one database write per request during a flood. See
  [Data for tuning](#data-for-tuning).

## Limits

Defaults (`ANON_RATE_LIMITS=40/10,150/60,5000/86400`): **40 requests per 10 s,
150 per minute, 5000 per day, per IP, all enforced together.**

They come from the production log analysis, 2025-12-20 → 2026-10-15
(393k requests):
- 41% of traffic comes from 182 IPs in USP's network (`143.107/16`). Those IPs
  are NATs; one of them carried 130 distinct users. The limits are therefore
  sized for the USP NAT, not for a typical user.
- The rule used: limit ≈ 3–4× the p99.9 of the USP NAT IPs, and never below
  the highest value observed.

| Window | p99.9 (USP NAT) | Highest observed | Limit |
|---|---|---|---|
| 10 s | ~14 | 38 | 40 |
| 1 min | 36 | 135 | 150 |
| 1 day | 1,426 | 1,580 | 5,000 |

Had these limits been live, no window in the analyzed period would have been
blocked.

Algorithm: **fixed window**. Each rule maps to a Redis key
`rl:ip:<ip>:<window>:<now // window>`, updated with `INCR` and `EXPIRE` in one
pipeline (a single round trip for all rules). IPv6 clients are grouped by
their **/64**, because one subscriber usually controls a whole /64 and could
otherwise rotate addresses to get around the limit.

Not counted:
- `OPTIONS` requests (CORS preflight);
- `/health`, `/docs`, `/redoc` and `/openapi.json`.

## Requests with an API key

A request with a valid `X-API-Key` (see `API_KEYS.md`) is counted against
**the key's own limits**, in the bucket `rl:key:<id>:...`, instead of the
per-IP ones. **Browser keys** are public, so each visitor **also** keeps the
per-IP limit: one client reusing a visible key can't burn the partner's
quota. Invalid keys never reach the limiter. `ApiKeyMiddleware` rejects them
first and cuts an IP off with 429 after 20 failures a minute.

## Request cost caps

Counting requests isn't enough: one unbounded request can cost more than
thousands of small ones. Date ranges are therefore capped, both ends
included, with **400** over the cap:

- **`/allocations/events`: 31 days.** It expands occurrences per day, and
  production traffic never asked for more than 14.
- **Every route using `QueryInterval`: 366 days.** Semester views of
  classes and reservations by building legitimately ask for about 365.
- Also rejected: `end` before `start`.

## Responses

- A blocked request gets **429** with `Retry-After` (seconds) and the body
  `{"detail": "Muitas requisições. Tente novamente em N segundos."}`.
- In `enforce` mode, **every** response carries `X-RateLimit-Limit`,
  `X-RateLimit-Remaining` and `X-RateLimit-Reset` (seconds until the window
  resets). The values come from the most restrictive rule.
- These headers are listed in CORS `expose_headers`, so browser JavaScript can
  read them.

## Data for tuning

The first request that goes over a rule (per IP, per window) produces **one
row** in `apiaccesslog`:

- `status_code = 429`;
- tags `RateLimit` and `RateLimit:enforce` (or `RateLimit:shadow`);
- the rule in `detail`: `"Rate limit: regra 150/60 excedida"`;
- IP, endpoint, method and user-agent.

The rest of the 429s in that same window are not persisted (the log line in
`api.log` is also written only once).

**In `shadow` mode** nothing is blocked, and the client receives the normal
response. The row still records a **429 that would have happened**. Its tag is
`RateLimit:shadow` and its `detail` ends with "(modo shadow, requisição não
bloqueada)", so it can be told apart from a real 429.

Queries for tuning (compare with the baseline in `~/dev/USPolis/data/analise_rate_limit.md`):

```sql
-- Which rules trip, and how often
SELECT detail, count(*) FROM apiaccesslog
WHERE 'RateLimit' = ANY(tags) AND timestamp > now() - interval '7 days'
GROUP BY detail ORDER BY count DESC;

-- Which IPs and routes (USP NAT = 143.107.*)
SELECT ip_address, endpoint, count(*) FROM apiaccesslog
WHERE 'RateLimit' = ANY(tags) AND timestamp > now() - interval '7 days'
GROUP BY ip_address, endpoint ORDER BY count DESC LIMIT 20;
```

Rows are removed by the daily purge after `ERROR_METRICS_RETENTION_DAYS`
(31 days by default), just like every other row in `apiaccesslog`.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `REDIS_URL` | empty | e.g. `redis://:<password>@127.0.0.1:6379/0`. Empty disables rate limiting, and an error is logged at startup if the mode is not `off`. |
| `RATE_LIMIT_MODE` | `off` | `off` \| `shadow` \| `enforce` |
| `ANON_RATE_LIMITS` | `40/10,150/60,5000/86400` | `max/window_seconds` rules, comma separated |

**Startup check:** each worker reports the rate-limit setup once at startup,
in `logs/api.log` and on the console:

| Situation | Message (level) |
|---|---|
| All good | `Rate limit: Redis OK at redis://:***@127.0.0.1:6379/0, mode=enforce, rules=40/10, 150/60, 5000/86400` (INFO) |
| Off | `Rate limit: disabled (RATE_LIMIT_MODE=off)` (INFO) |
| Redis down | `Rate limit: Redis unreachable at ... ; requests pass unlimited until it is back (fail-open)` (ERROR) |
| No `REDIS_URL` | `Rate limit: RATE_LIMIT_MODE=enforce but REDIS_URL is empty, rate limiting disabled (fail-open)` (ERROR) |
| Invalid value | `Rate limit: invalid config, rate limiting disabled (...)` (ERROR) |

The password in `REDIS_URL` is always masked. In the test suite (`CONFIG.testing`),
rate limiting is **always off**, whatever the `.env` says, so a developer's
`RATE_LIMIT_MODE=enforce` can't turn API tests into 429s.

**Fail-open:** if Redis is down or slow (0.2 s timeout), requests go through.
An error is logged at most once a minute per worker. Availability wins over
limiting.

## Client IP: required for the limit to make sense

The limiter keys on `scope["client"]`, which Uvicorn resolves from
`X-Forwarded-For` **only when the request comes from an address listed in
`--forwarded-allow-ips`**. `get_client_ip` (used by the logs) uses the same
value. The raw header is never read, since a client could forge it.

- **systemd deploy (current):** `--forwarded-allow-ips="127.0.0.1"`, which is
  correct because Nginx runs on the same host.
- **Docker:** in the `USPolis-Admin` compose file, `GUNICORN_FORWARDED_ALLOW_IPS`
  is the gateway of the fixed subnet (`172.28.0.1`), since Nginx reaches the
  container through Docker's port proxy.
- **Nginx** must set `proxy_set_header X-Forwarded-For $remote_addr;`
  (overwrite, not append).

⚠️ If this is misconfigured, every request appears to come from a single IP
(the proxy's), and the first busy minute blocks everyone. That is one of the
reasons to roll out in `shadow` mode first.

## Rollout

1. **Redis** on the VM (see below) and `REDIS_URL` in `.env.prod`.
2. **`RATE_LIMIT_MODE=shadow`** for 1–2 weeks, including a busy period if
   possible. Nothing is blocked; each IP that exceeds a rule produces **one**
   line per window:
   ```
   [2026-10-20 14:03:11] WARNING type="RateLimit" mode="shadow" host="143.107.x.x" method="GET" path="/allocations/events" rule="150/60"
   ```
3. Review the lines:
   ```bash
   grep 'type="RateLimit"' logs/api.log | grep -o 'rule="[^"]*"' | sort | uniq -c
   grep 'type="RateLimit"' logs/api.log | grep -o 'host="[^"]*"' | sort | uniq -c | sort -rn | head
   ```
   - If every line shows the same `host`, the client IP is wrong (see the
     previous section). **Do not switch to enforce.**
   - If legitimate IPs (USP NAT) show up, raise the rule in question in
     `ANON_RATE_LIMITS`.
4. **`RATE_LIMIT_MODE=enforce`**. To roll back immediately, set `off` and
   restart the service.

## Redis on the VM (systemd deploy)

```bash
sudo apt install redis-server
sudo nano /etc/redis/redis.conf
```

Settings in `redis.conf`:

```
bind 127.0.0.1 -::1          # local only
protected-mode yes
requirepass <long-random-password>
maxmemory 64mb               # rate-limit counters use < 30 MB
maxmemory-policy volatile-ttl
save ""                      # no persistence: counters are ephemeral
appendonly no
```

```bash
sudo systemctl enable --now redis-server
sudo systemctl restart redis-server
REDISCLI_AUTH='<password>' redis-cli ping      # -> PONG
```

Then, in `.env.prod`:

```
REDIS_URL=redis://:<password>@127.0.0.1:6379/0
RATE_LIMIT_MODE=shadow
```

If the password has special characters, URL-encode it in `REDIS_URL`.

Restart the backend (`sudo systemctl restart uspolis-backend`) and check that
counter keys appear:

```bash
REDISCLI_AUTH='<password>' redis-cli --scan --pattern 'rl:*' | head
```

## Docker deploy

The `USPolis-Admin` compose file already provides:
- a `redis` service (`redis:7.4-alpine`, password, `maxmemory`, no
  persistence, no published port, CPU and memory limits);
- `REDIS_URL` and `GUNICORN_FORWARDED_ALLOW_IPS` for the backend;
- the backend port bound to `127.0.0.1`.

`RATE_LIMIT_MODE` goes in the compose `.env`.

## Tests

- `tests/unit/services/test_rate_limiter.py` covers rule parsing, IP identity,
  the windows, multiple rules and fail-open. It uses `fakeredis`.
- `tests/unit/middlewares/test_rate_limit_middleware.py` covers the 429,
  headers, separate IPs, ignoring a forged `X-Forwarded-For`, exempt paths,
  `OPTIONS`, `shadow`, `off` and Redis being down.
