# API Keys

How partners (e.g. the student association's website) get read access to
public USPolis data: the data model, the key format, and the rules USPolis
follows when issuing and handling keys.

**Status:** every phase is done.
- Phase 1: tables, key format, repositories.
- Phase 2: admin routes.
- Phase 4: keys accepted on public routes, with their own limits.
- Phase 5: CORS for browser-key origins; date-range caps.

The guide to hand to partners is [`PARTNER_API.md`](PARTNER_API.md)
(Portuguese).

The plan lives in `sdd/plans/api-keys-and-rate-limit.md`.

## Model

```
user ─┬─< apiclient (created_by)
      └─< apikey (created_by / revoked_by)
apiclient ─< apikey ─< apikeyratelimit
```

- **`ApiClient`** (`apiclient`) is the partner, not a USPolis user.
  - Required contact (`contact_name`, `contact_email`): someone to warn about
    leaks and expiring keys.
  - `is_active=false` rejects **all** of the client's keys at once.
- **`ApiKey`** (`apikey`) belongs to one client. Multiple keys per client
  allow rotation and one key per app or environment.
  - `public_id` identifies the key without revealing it.
  - `key_hash` is the HMAC of the key, the only thing stored.
  - `allowed_path_prefixes` sets the scope.
  - `allowed_origins`, when non-empty, makes it a browser key.
  - `expires_at` is required, at most 365 days out.
  - `revoked_at` / `revoked_by_id` / `revoked_reason`: revocation is final.
    The row stays for the audit trail.
- **`ApiKeyRateLimit`** (`apikeyratelimit`) holds 0..N
  `max_requests/window_seconds` rules per key, all enforced together. With
  none, the defaults apply, so a key is never unlimited:
  - `API_KEY_DEFAULT_LIMITS=30/10,120/60,10000/86400` for server keys;
  - `API_KEY_BROWSER_DEFAULT_LIMITS=60/10,300/60,20000/86400` for browser
    keys. This is higher because one browser key is shared by every visitor
    of the partner's site. The per-IP anonymous limit still applies to each
    visitor, so a single client can't exhaust it.

The database enforces the invariants, even if code skips the request
validators:
- a key has at least one path prefix;
- `revoked_by_id` requires `revoked_at` (the reverse is allowed: an
  automatic revocation, or the revoking admin was deleted);
- `expires_at > created_at`;
- each window appears only once per key;
- limits are positive.

Deleting a client cascades to its keys and their limits.

## Key format

```
up_<env>_<public_id>_<secret>_<checksum>
up_live_a1b2c3d4e5f60718_<43 base62 chars>_<6 base62 chars>
```

| Field | Content | Why |
|---|---|---|
| `up` | prefix | Identifies a USPolis key at a glance and for scanners. |
| `env` | `live` (production), `test` (staging), `dev` (development) | A server only accepts keys of its own `ENVIRONMENT`. A leaked `test`/`dev` key is low-risk. |
| `public_id` | 16 hex chars | Lookup id, and safe to show in admin screens and logs. |
| secret | 43 base62 chars, ≈ 256 bits | The secret part. |
| checksum | CRC32 of the rest, 6 base62 chars | Rejects typos and truncation **without a DB lookup**; lets scanners confirm a match. It is **not** a security control. |

Validation order (cheapest first): shape → `env` → checksum → DB lookup by
`public_id` → HMAC comparison (constant time). Every failure gives the same
response.

**Scanner regex** (`API_KEY_PATTERN` in
`server/services/security/api_key_crypto.py`). Share it with partners for
gitleaks, trufflehog or GitHub custom patterns:

```
\bup_(live|test|dev)_[0-9a-f]{16}_[0-9A-Za-z]{43}_[0-9A-Za-z]{6}\b
```

**Storage:** only `HMAC-SHA256(API_KEY_SECRET, full key)` is stored. A slow
password hash (bcrypt) buys nothing for 256-bit random keys and would cost CPU
on every request. The server-side secret means a leaked database dump can't
be used to verify guesses. `hash_version` records which secret produced each
hash, so `API_KEY_SECRET` can be rotated gradually: add the new version for
new keys, and drop the old one once its keys expire. To invalidate every key
at once (for example, the secret itself leaked), remove the old version
immediately.

## Admin routes

Admin only (`/api/admin/...`, `admin_authenticate`). There is **no DELETE**:
deactivate a client or revoke a key instead, so the audit trail is kept.

| Method | Path | What |
|---|---|---|
| GET | `/admin/api-clients` | List clients, with `active_keys` / `total_keys` |
| POST | `/admin/api-clients` | Create a client (201; 409 if the name is taken, case-insensitive) |
| GET | `/admin/api-clients/{id}` | One client |
| PUT | `/admin/api-clients/{id}` | Edit name, contact, description |
| PATCH | `/admin/api-clients/{id}/active` | `{"is_active": false}` disables **all** its keys at once |
| GET | `/admin/api-clients/{id}/keys` | The client's keys, newest first |
| POST | `/admin/api-clients/{id}/keys` | Issue a key (201). **The only response that contains the key** (`key` field), sent with `Cache-Control: no-store` |
| GET | `/admin/api-keys/{id}` | One key (masked) |
| PUT | `/admin/api-keys/{id}` | Edit name, prefixes, origins, expiry (409 if revoked) |
| PUT | `/admin/api-keys/{id}/rate-limits` | Replace its limits; `{"rate_limits": []}` = back to the defaults |
| PATCH | `/admin/api-keys/{id}/revoke` | `{"reason": "..."}`, final (409 if already revoked) |

Key responses never include the key or its hash. They include:
- `masked_key`: `up_<env>_<public_id>_****`;
- `key_type`: `server` or `browser`;
- `status`: `active`, `expired`, `revoked` or `client_inactive`, in that
  precedence: `revoked` beats `client_inactive`, which beats `expired`;
- the limits **actually enforced**, with `uses_default_limits` saying whether
  they're the configured defaults.

A test asserts that issuing a key never writes it to the logs.

## Delivery by one-time link ("Entrega por link")

Instead of copying the key out of the admin screen and pasting it into a
chat or an email, where it stays forever, the admin can issue it **by
link**. The partner opens the link, clicks **Revelar chave** and sees the
key **once**. In this mode the admin never sees the key.

### How it works

1. `POST /admin/api-clients/{id}/keys/via-link` issues the key as usual
   (only its HMAC goes into `apikey`) and **seals** the plaintext into an
   `apikeydeliverylink` row:
   - a random 256-bit `token` is generated and **never stored**;
   - HKDF-SHA256(`token`, random `salt`) derives an AES-256 key;
   - AES-256-GCM encrypts the key, with a random `nonce` and the link's
     `link_id` as associated data (binding the ciphertext to its row).

   The row keeps `ciphertext`, `nonce` and `salt`. A database dump, even
   with `API_KEY_SECRET`, can't open it: only the URL has the token.
2. The response has the link: `<FRONTEND_URL>/api-key/<link_id>#<token>`. The
   token is in the **fragment**, which browsers never send to a server, so
   it stays out of Nginx logs, the access log and `Referer` headers.
3. The partner's page calls `GET /api-key-links/{link_id}` for the status.
   **GET never consumes the link**: chat apps and email scanners fetch links
   to build previews.
4. On the click, the page POSTs the token from the fragment to
   `/api-key-links/{link_id}/reveal`. The row is locked
   (`SELECT ... FOR UPDATE`) so two concurrent reveals can't both succeed;
   the sealed fields are wiped and `consumed_at`/IP/user agent recorded.
5. A wrong token is a 404 that **changes nothing**: `link_id` is in the
   logs, and reading them must not be enough to burn the link. With 256-bit
   tokens guessing is hopeless; the per-IP limits cover the rest.

A link nobody opened is a key nobody has, so **killing an unopened link
revokes its key**: invalidating it, or letting it expire (the daily task
`expire_api_key_links` wipes and revokes those). Revoking the key also kills
its pending link. Rows are never deleted: who issued, emailed and opened
each link stays in the audit trail.

### Routes

| Method | Path | What |
|---|---|---|
| POST | `/admin/api-clients/{id}/keys/via-link` | Body of a key issue plus `link_ttl_hours` (1, 24 or 72; default 24). 201 with `key` (masked), `link`, `token` and `url`, `Cache-Control: no-store`. **No plaintext key** |
| PATCH | `/admin/api-key-delivery-links/{id}/invalidate` | Kill a link that wasn't opened yet and revoke its key (410 if already used or invalidated) |
| POST | `/admin/api-keys/{id}/share-link/email` | `{"token": "...", "message": "..."}`: email the link (never the key) to the client's `contact_email` |
| GET | `/api-key-links/{link_id}` | Public status: `status`, `available`, `expires_at`, client and key names. No secret |
| POST | `/api-key-links/{link_id}/reveal` | `{"token": "..."}`: the key, once. 404 unknown link or wrong token; 410 used, expired, invalidated, or key revoked / client inactive |

Key responses carry `delivery_link` (status, expiry, who opened it and
when, last email) when the key was issued by link. Public responses are sent
with `Cache-Control: no-store`, `Referrer-Policy: no-referrer` and
`X-Robots-Tag: noindex`.

### Emailing the link

The server never stores the token, so it **can't rebuild the link** once
the creation response is gone. The admin's screen holds the token and sends
it back to `share-link/email`, which:
- checks it by decrypting, without consuming the link (404 if wrong, 410 if
  the link is no longer pending);
- builds the URL itself from `FRONTEND_URL`, never from client input, so the
  official email can't be made to point anywhere else;
- sends only to the client's `contact_email` (outside production, to
  `SYSTEM_LIST`, like every other email);
- sends synchronously and answers **502** if SMTP fails, recording nothing:
  unlike notification emails, the admin must know the partner got it.

Once the modal closes, the token is gone: to send again, invalidate the
link and issue a new key. A link in an email is safer than the key: it
expires, works once, and if someone else opens it first the partner sees
"já aberto" and tells us, so the key gets revoked.

The token is in `SENSITIVE_BODY_KEYS`, so it is redacted from logged and
persisted request bodies.

## Using a key

The partner sends the key in a header, on **GET/HEAD requests to public
routes** only:

```bash
curl -H "X-API-Key: up_live_..." https://uspolis.com.br/api/allocations/events?start=2026-10-17&end=2026-10-17
```

**How a request is handled** (`ApiKeyMiddleware` in `server/middlewares/api_key_middleware.py`):

1. A request without `X-API-Key` is **anonymous**, as before, under the
   per-IP limit.
2. `?api_key=` (or `apikey`, `x-api-key`) in the URL → **400**, even without
   the header. The URL ends up in logs and browser history.
3. If the IP already has 20 failed key attempts in the current minute →
   **429**, without even looking the key up. This stops guessing from
   flooding the database or the logs.
4. Then the key is checked, cheapest first:
   - shape, `env` and checksum (no I/O);
   - the record (Redis cache, otherwise DB);
   - hash (constant time);
   - revoked, client inactive, expired → **401**;
   - not GET/HEAD, not a public route, outside `allowed_path_prefixes`, or
     wrong `Origin` → **403**.
   A bad key **never** falls back to anonymous.
5. A valid key is counted against **its own limits** instead of the per-IP
   one. Browser keys also keep the per-IP limit for each visitor. Limits are
   enforced only when `RATE_LIMIT_MODE=enforce`; `shadow` only logs.

**What the client sees:**

| Status | Body (`detail`) | Notes |
|---|---|---|
| 400 | "Envie a API key no header X-API-Key, nunca na URL." | key in the query string |
| 401 | "API key inválida, expirada ou revogada." | same body for every reason; `WWW-Authenticate: ApiKey` |
| 403 | "Esta API key não tem permissão para esta requisição." | same body for every reason |
| 429 | "Muitas requisições…" / "Muitas tentativas com API key inválida…" | `Retry-After`, `X-RateLimit-*` |
| 503 | "API keys estão temporariamente indisponíveis." | `API_KEY_SECRET` missing on the server |

The real reason is only in `logs/api.log`, with the `public_id` and never the
key:

```
WARNING type="ApiKeyRejected" status="401" host="..." method="GET" path="/buildings" public_id="a1b2c3d4e5f60718" reason="revoked"
```

**Cache and revocation.**
- The key record is cached in Redis for 60 s (`apikey:<public_id>`), and
  unknown ids are cached too.
- Every admin change deletes the entry immediately, so **revoking or
  deactivating takes effect on the next request**. The changes that do this:
  editing the key, changing its limits, revoking it, or (de)activating its
  client.
- If Redis is down, every request reads the DB. If the delete fails, the entry
  still expires within 60 s.

**`last_used_at`** is written at most once a minute per key (a Redis `SET NX`
guards it). Without Redis it isn't updated.

**Audit:** rows persisted in `apiaccesslog` carry `api_key_id`. That covers
errors (≥400 except 401/429) and the first 429 of each window. Key
rejections themselves (401/403) go to `api.log`, capped by the per-IP failure
limit.

## Browser keys and CORS

`PartnerCorsMiddleware` (`server/middlewares/partner_cors_middleware.py`)
serves the CORS of partner sites. It sits **outside** Starlette's
`CORSMiddleware`, because that one rejects any preflight from an origin not in
`ALLOWED_ORIGINS`. The full chain is Logger → PartnerCors → CORS → ApiKey →
RateLimit.

- **Who gets it:** the origins of **usable browser keys** (not revoked, not
  expired, active client), and only for **GET/HEAD on public routes**.
- **No credentials, ever.** The inner `CORSMiddleware` adds
  `Access-Control-Allow-Credentials: true` to every response, even for
  origins it doesn't allow. PartnerCors strips it from partner responses;
  otherwise a partner page could send our users' session cookie. A test
  covers this.
- **First-party origins** (`ALLOWED_ORIGINS`) behave exactly as before,
  credentials included.
- **Origins cache:** the list is cached **in memory, per worker, for 30 s**,
  so random `Origin` headers can't trigger a DB query per request. A new or
  revoked browser key's site is picked up within 30 s. CORS only lets the
  browser read the response; the real gate is `ApiKeyMiddleware`, which
  checks the `Origin` against the key itself on every request, immediately.
- **If loading the origins fails**, the middleware fails closed: no partner
  CORS, and an error is logged.

## Rules USPolis follows

✅ = enforced in code · 📋 = process.

1. **Plaintext keys are never stored or logged.**
   - ✅ Only the HMAC is persisted, and the repository returns the plaintext
     exactly once, at creation.
   - ✅ Headers are never logged, and any key that shows up in a logged URL is
     masked (`[REDACTED_API_KEY]`). A test asserts that issuing a key never
     logs it.
   - ✅ Keys are accepted only in the `X-API-Key` header; a key in the query
     string gets 400.
2. **`API_KEY_SECRET`.**
   - 📋 32+ random bytes, different per environment, only in env or a secret
     store, never committed. Generate one with
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
   - ✅ Generating or verifying a key fails if it's missing or too short.
   - ✅ Each worker reports at startup whether it can verify keys
     (`API keys: ready…` or an error).
3. **Delivery.**
   - ✅ Built in: issue the key by one-time link (`/keys/via-link`, see
     "Delivery by one-time link"); the admin never sees it, and the link
     can be emailed by the API or pasted into a chat.
   - 📋 With a key issued directly, send the plaintext in person or through
     a one-time-secret tool, never by plain email or chat.
   - ✅ Issuance is audited (`created_by_id`), and the creation response is sent with `Cache-Control: no-store`.
4. **Least privilege.**
   - ✅ GET/HEAD only, public-tier routes only (matched by the `Public` tag,
     even with prefix `/`), never a user identity.
   - 📋 Use the narrowest prefixes possible; `"/"` needs a written
     justification.
   - 📋 One key per partner app per environment, never shared between
     partners.
5. **Every key has a lifetime and a limit.**
   - ✅ `expires_at` is required, at most 365 days.
   - ✅ A key without limit rows falls back to the defaults.
   - 📋 Review keys every quarter; revoke any unused for 90+ days
     (`last_used_at`).
6. **Browser keys are public by nature.**
   - ✅ Origins must be HTTPS (`http://localhost` only outside production),
     with no wildcards or paths.
   - ✅ The request's `Origin` must be in the key's list.
   - ✅ The per-IP anonymous limit also applies to them.
   - ✅ Server keys (no origins) are rejected when an `Origin` header is
     present.
7. **Leaks.**
   - 📋 Revoke immediately, notify `contact_email`, then reissue.
   - ✅ Revocation is final, and `is_active=false` disables all of a
     client's keys at once.
8. **No oracle for attackers.**
   - ✅ Unknown, revoked, expired and wrong-origin keys all get the same
     generic response. The real reason is logged with `public_id`.
   - ✅ Repeated failures from one IP are cut off with 429.
   - ✅ Hash and checksum comparisons are constant time.
9. **Data exposure (LGPD).** 📋 Before opening a route to partners, check its
   response for personal data (names, emails, USP numbers).
10. **Transport and edge.**
    - ✅ The client IP comes only from trusted proxies (see `RATE_LIMIT.md`).
    - 📋 HTTPS with HSTS at Nginx.
11. **Monitoring.**
    - ✅ Persisted `apiaccesslog` rows carry `api_key_id`, and rejections are
      logged with `public_id` and reason.
    - 📋 Alert on spikes of invalid keys or 429s per `public_id`.

## Code

| What | Where |
|---|---|
| Tables | `server/models/database/api_{client,key,key_rate_limit,key_delivery_link}_db_model.py` |
| Key generation, parsing, hashing | `server/services/security/api_key_crypto.py` |
| Sealing keys for delivery links | `server/services/security/api_key_link_crypto.py` |
| Prefix and origin rules | `server/services/security/api_key_scope.py` |
| Request validation | `server/models/http/requests/api_key_request_models.py` |
| Repositories | `server/repositories/api_{client,key,key_delivery_link}_repository.py` |
| Admin routes | `server/routes/admin/api_key_admin_routes.py` |
| Public delivery-link routes | `server/routes/public/api_key_link_routes.py` |
| Link email | `EmailService.send_api_key_link_email`, `server/templates/api_keys/api-key-link.html` |
| Expiring unopened links | `expire_api_key_links` in `server/services/cron/daily_tasks.py` |
| Request authentication, cache, `last_used_at` | `server/services/security/api_key_auth.py`, `ApiKeyMiddleware` in `server/middlewares/api_key_middleware.py` |
| Responses, status, effective limits | `server/models/http/responses/api_key_response_models.py`, `server/services/security/api_key_limits.py` |
| Migrations | `migrations/versions/563e00883007_create_api_client_key_and_rate_limit_.py`, `migrations/versions/8feb53242f11_add_api_key_delivery_link.py` |
| Tests | `tests/unit/services/security/test_api_key_*.py`, `tests/unit/models/**/test_api_key_*.py`, `tests/integration/repositories/test_api_{client,key}_repository.py`, `tests/api/admin/test_api_key_admin_routes.py`; links: `tests/unit/services/security/test_api_key_link_crypto.py`, `tests/integration/repositories/test_api_key_delivery_link_repository.py`, `tests/api/{admin,public}/test_api_key_link*_routes.py`, `tests/integration/services/test_expire_api_key_links.py` |
