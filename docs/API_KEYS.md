# API Keys

How partners (e.g. the student association's website) get read access to
public USPolis data: the data model, the key format, and the rules USPolis
follows when issuing and handling keys.

**Status:**
- Phase 1 (tables, key generation and hashing, repositories) is done.
- Phase 2 (admin routes, below) is done.
- Keys can't be used to call the API yet. That comes with Phase 4: the
  `X-API-Key` dependency that validates keys and applies their limits.

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

## Rules USPolis follows

✅ = enforced in code today · ⏳ = enforced when its phase lands ·
📋 = process.

1. **Plaintext keys are never stored or logged.**
   - ✅ Only the HMAC is persisted, and the repository returns the plaintext
     exactly once, at creation.
   - ⏳ `X-API-Key` is redacted from logs (Phase 4).
   - ⏳ Keys are accepted only in the `X-API-Key` header, never in the query
     string, because URLs end up in logs and browser history (Phase 4).
2. **`API_KEY_SECRET`.**
   - 📋 32+ random bytes, different per environment, only in env or a secret
     store, never committed. Generate one with
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
   - ✅ Generating or verifying a key fails if it's missing or too short.
   - ⏳ A startup check comes with Phase 4.
3. **Delivery.**
   - 📋 Send the plaintext through a one-time-secret link or in person, never
     by plain email or chat.
   - ✅ Issuance is audited (`created_by_id`), and the creation response is sent with `Cache-Control: no-store`.
4. **Least privilege.**
   - ⏳ GET/HEAD only, public tier only, never a user identity.
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
   - ⏳ The per-IP anonymous limit also applies to them.
   - ⏳ Server keys (no origins) are rejected when an `Origin` header is
     present.
7. **Leaks.**
   - 📋 Revoke immediately, notify `contact_email`, then reissue.
   - ✅ Revocation is final, and `is_active=false` disables all of a
     client's keys at once.
8. **No oracle for attackers.**
   - ⏳ Unknown, revoked, expired and wrong-origin keys all get the same
     generic response. The real reason is logged with `public_id`.
   - ✅ Hash and checksum comparisons are constant time.
9. **Data exposure (LGPD).** 📋 Before opening a route to partners, check its
   response for personal data (names, emails, USP numbers).
10. **Transport and edge.**
    - ✅ The client IP comes only from trusted proxies (see `RATE_LIMIT.md`).
    - 📋 HTTPS with HSTS at Nginx.
11. **Monitoring.**
    - ⏳ The key is recorded on rejected requests in `apiaccesslog`.
    - 📋 Alert on spikes of invalid keys or 429s per `public_id`.

## Code

| What | Where |
|---|---|
| Tables | `server/models/database/api_{client,key,key_rate_limit}_db_model.py` |
| Key generation, parsing, hashing | `server/services/security/api_key_crypto.py` |
| Prefix and origin rules | `server/services/security/api_key_scope.py` |
| Request validation | `server/models/http/requests/api_key_request_models.py` |
| Repositories | `server/repositories/api_{client,key}_repository.py` |
| Admin routes | `server/routes/admin/api_key_admin_routes.py` |
| Responses, status, effective limits | `server/models/http/responses/api_key_response_models.py`, `server/services/security/api_key_limits.py` |
| Migration | `migrations/versions/563e00883007_create_api_client_key_and_rate_limit_.py` |
| Tests | `tests/unit/services/security/test_api_key_*.py`, `tests/unit/models/**/test_api_key_*.py`, `tests/integration/repositories/test_api_{client,key}_repository.py`, `tests/api/admin/test_api_key_admin_routes.py` |
