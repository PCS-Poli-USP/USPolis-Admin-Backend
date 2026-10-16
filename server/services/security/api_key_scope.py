"""Path-prefix and origin rules for partner API keys (see docs/API_KEYS.md).

Paths are relative to the app root (`/api` is stripped), e.g. `/allocations`.
"""
 
from urllib.parse import urlsplit

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def path_matches_prefix(path: str, prefix: str) -> bool:
    """Whole-segment match: `/allocations` covers `/allocations` and
    `/allocations/events`, but not `/allocationsx`. `/` covers everything."""
    if prefix == "/":
        return True
    return path == prefix or path.startswith(prefix + "/")


def path_allowed(path: str, prefixes: list[str]) -> bool:
    return any(path_matches_prefix(path, prefix) for prefix in prefixes)


def validate_path_prefix(prefix: str) -> str:
    """Reject anything but a clean absolute path; raises ValueError."""
    if not prefix.startswith("/"):
        raise ValueError(f"O prefixo {prefix!r} deve começar com '/'")
    if prefix != "/" and prefix.endswith("/"):
        raise ValueError(f"O prefixo {prefix!r} não pode terminar com '/'")
    if "//" in prefix or any(part in (".", "..") for part in prefix.split("/")):
        raise ValueError(f"O prefixo {prefix!r} contém segmentos inválidos")
    if any(char in prefix for char in "?#*%\\ "):
        raise ValueError(f"O prefixo {prefix!r} contém caracteres inválidos")
    return prefix


def validate_origin(origin: str, *, allow_insecure_localhost: bool) -> str:
    """Normalize and validate a browser Origin (`scheme://host[:port]`);
    raises ValueError. Only https, except http://localhost when allowed.

    Valid: `https://gremio.poli.usp.br`, `https://site.com:8443`, and
    `http://localhost:3000` (only with `allow_insecure_localhost`).
    `https://Site.com/` is normalized to `https://site.com`.
    Invalid: `http://site.com`, `https://*.usp.br`, `https://site.com/path`."""
    origin = origin.strip().rstrip("/").lower()
    if "*" in origin:
        raise ValueError(f"A origem {origin!r} não pode conter curingas")
    parts = urlsplit(origin)
    if not parts.hostname or parts.path or parts.query or parts.fragment:
        raise ValueError(f"A origem {origin!r} deve ser apenas esquema://host[:porta]")
    if parts.username or parts.password:
        raise ValueError(f"A origem {origin!r} não pode conter credenciais")
    is_local = parts.hostname in LOCAL_HOSTS
    if parts.scheme == "https":
        return origin
    if parts.scheme == "http" and is_local and allow_insecure_localhost:
        return origin
    raise ValueError(f"A origem {origin!r} deve usar https")
