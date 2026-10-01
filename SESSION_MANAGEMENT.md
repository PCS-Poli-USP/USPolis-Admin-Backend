# Session Management

How login sessions work end to end: the `session` cookie, the `UserSession`
table, and the two expiration mechanisms that gate whether a cookie still
authenticates.

## The cookie

Set by `/auth/get-tokens` and `/auth/refresh-token` (`server/routes/public/auth_routes.py`):

```python
response.set_cookie(
    key="session",
    value=user_session.id,
    httponly=True,
    secure=True,
    samesite="none" if CONFIG.development else "lax",
    max_age=SESSION_COOKIE_AGE,  # 30 days
    path="/",
)
```

The cookie value is the `UserSession.id` (a UUID hex). It's opaque to the
browser — it's only meaningful as a lookup key against the `UserSession`
table server-side. `httponly` keeps it invisible to JS (XSS can't read it
directly); `secure` requires a real HTTPS connection to be stored at all.

This app assumes **same-origin deployment**: the frontend and the API are
served from the same host, with a reverse proxy (nginx) routing `/api/*` to
this backend and everything else to the frontend. That's why `samesite="lax"`
outside of development is fine — there's no cross-site request involved, so
CORS and SameSite cross-site restrictions never come into play for this
cookie in production/staging.

## Authentication from the cookie

`server/deps/authenticate.py`:

- `authenticate()` (required) / `public_authenticate()` (optional) both try a
  bearer token first, then fall back to the cookie via
  `authenticate_from_cookie()` / `public_authenticate_from_cookie()`.
- Both cookie-auth functions look up the `UserSession` row by id and reject
  it (treat as unauthenticated) if `UserSession.is_expired()` is `True` —
  i.e. `expires_at < now`.

This is deliberately the **only** thing that determines whether a session is
still valid. There's no separate revocation flag or blocklist — a session is
valid exactly as long as `expires_at` is in the future.

## Session identity: what counts as "the same session"

`/auth/get-tokens` (a real interactive login) first checks whether the
browser already sent a live `session` cookie for the user who just
authenticated with Google — `UserSessionRepository.get_valid_session_for_renewal()`
looks the cookie's id up by primary key, and only accepts it if it belongs to
this `user_id`, isn't expired, and hasn't hit the absolute max age. That's
the common case (same browser, cookie still valid) and needs no heuristics
at all.

Only when there's no usable cookie — first login on this browser, or the
cookie was rejected above — does the code fall back to
`UserSessionRepository.get_session()`, which looks up an existing row by
`(user_id, user_agent)`. This is an **application-level lookup, not a
database uniqueness constraint** — nothing prevents two rows with the same
pair from existing simultaneously; it's just how the fallback decides
whether to reuse a row or create a new one.

`ip_address` is **not** part of either lookup — it's stored on the row as
descriptive metadata only (shown in the admin sessions view), never used to
decide session identity. It was dropped from the matching key because it
changes far more often than the browser/OS does — VPNs, university or
carrier NAT subnets, and switching networks (wifi vs mobile data) all rotate
a user's visible IP without it being a different device or a different
session in any meaningful sense. Keeping it in the lookup meant those users
accumulated a fresh orphaned `UserSession` row on every network change
instead of renewing the one they already had.

Practical consequence of the remaining `user_agent` fallback: if a user
switches browsers, or a browser upgrade changes its user-agent string,
between logins with no valid cookie in hand, the lookup won't match the old
row, and a brand new `UserSession` is created — the old row stays in the
table, unused, until it expires or is explicitly deleted (logout, or an
admin action via `GET/DELETE /admin/sessions/users`).

## Expiration: two mechanisms

### 1. Sliding window — `SESSION_DURATION_DAYS` (30 days)

Every time a session is renewed — via a fresh login (`/auth/get-tokens`) or a
silent token refresh (`/auth/refresh-token`) — `UserSessionRepository.extend_session()`
pushes `expires_at` to `now + 30 days`. As long as the session keeps getting
renewed, it never expires. This is what makes "stay logged in while you keep
using the app" work.

### 2. Absolute cap — `SESSION_MAX_AGE_DAYS` (90 days)

Without a cap, mechanism 1 alone means a session **never truly expires** as
long as something keeps renewing it — including a silent background refresh
call that fires just because a tab is open, with no real user interaction.
That's a meaningful exposure window if the cookie or the device is ever
compromised (stolen cookie, shared/forgotten-logged-in computer): the
attacker's access would never lapse either.

`SESSION_MAX_AGE_DAYS` bounds this: `UserSessionRepository._capped_expiry()`
computes `min(now + SESSION_DURATION_DAYS, created_at + SESSION_MAX_AGE_DAYS)`
every time a session would be extended, so `expires_at` can never move past
`created_at + 90 days`, no matter how many times it's renewed. Once that
point passes, further renewal attempts are a no-op — `expires_at` stays
frozen in the past, `UserSession.is_expired()` starts returning `True`, and
the cookie stops authenticating.

**This enforcement is deliberately asymmetric between the two renewal paths:**

| Flow | Method | Behavior once `has_reached_max_age()` |
|---|---|---|
| `/auth/get-tokens` (real interactive Google login) | `UserSessionRepository.start_or_renew_session()` | Discards the maxed-out row and creates a **fresh** one (`created_at` resets) |
| `/auth/refresh-token` (silent, no fresh Google consent) | `extend_session()` directly | Extension is a no-op — session stays expired |

Only a genuine interactive login is allowed to reset the 90-day clock. If the
silent refresh path could also reset it, the absolute cap would be
meaningless — a background timer would renew it forever without the user
ever proving they're still the one behind the keyboard. The practical effect:
once a session passes 90 days old, the next silent refresh keeps working for
*that open tab* (Google's own access/refresh token lifecycle is independent
of ours), but any **new** tab or window — which has no in-memory token and
depends entirely on the cookie — will be rejected and forced through a real
login, which then starts a brand new 90-day-capped session.

## Known limitations / not handled here

- No cleanup job for expired `UserSession` rows — they linger in the table
  until deleted via logout, an admin action, or a future renewal attempt
  that replaces them. They're harmless (already rejected by `is_expired()`)
  but do accumulate.
- No user-facing "your active sessions" view — only the admin route
  (`GET /admin/sessions/users`) lists all sessions across all users.
- No cookie/session-id rotation on renewal — the same `UserSession.id` (and
  therefore the same cookie value) is reused across the sliding-window
  renewals; only `expires_at`/`created_at` change.
