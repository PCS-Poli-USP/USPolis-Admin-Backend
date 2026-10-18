"""CSRF defense for cookie-authenticated requests.

The browser attaches the `session` cookie to every request to the API, no
matter which page issued it. `SameSite=Lax` (production) already keeps it off
cross-site POST/PUT/PATCH/DELETE, but "site" is the registrable domain: any
`*.uspolis.com.br` page counts as same-site, and development uses
`SameSite=None`. So on top of that, a state-changing request authenticated
by the cookie must come from a page whose `Origin` we trust.

Bearer tokens and partner API keys are unaffected: a third-party page can't
attach those headers, so they can't be forged cross-site.

Safe methods (GET/HEAD/OPTIONS) are not checked: they must never change
state, since `SameSite=Lax` still sends the cookie on top-level cross-site
GET navigations.
"""

from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status

from server.config import CONFIG

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _origin_of(url: str) -> str | None:
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return None
    return f"{parts.scheme}://{parts.netloc}"


def request_origin(request: Request) -> str | None:
    """The `Origin` header, falling back to the origin of `Referer`.
    Browsers always send `Origin` on non-GET requests; "null" (sandboxed
    iframes, file://) counts as missing."""
    origin = request.headers.get("origin")
    if origin and origin != "null":
        return origin.rstrip("/")
    referer = request.headers.get("referer")
    return _origin_of(referer) if referer else None


def is_trusted_cookie_request(request: Request) -> bool:
    """Whether the session cookie may authenticate this request.

    Trusted: safe methods; an `Origin` listed in ALLOWED_ORIGINS; or a
    same-origin request (`Origin` host == `Host`, so any hostname the app is
    served on works without listing it). A page on another subdomain sends
    its own host in `Origin` and fails both. No origin at all is rejected:
    every browser sends one on these methods, and non-browser clients have
    no user's cookie to begin with."""
    if request.method in SAFE_METHODS:
        return True
    origin = request_origin(request)
    if origin is None:
        return False
    allowed = {o.rstrip("/") for o in CONFIG.allowed_origins}
    if origin in allowed:
        return True
    host = request.headers.get("host")
    return host is not None and urlsplit(origin).netloc == host


class UntrustedOriginForCookie(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origem da requisição não permitida para sessão por cookie",
        )
