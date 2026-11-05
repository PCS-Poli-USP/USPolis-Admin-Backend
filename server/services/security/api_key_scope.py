"""Path-prefix rules for partner API keys (see docs/API_KEYS.md).

Paths are relative to the app root (`/api` is stripped), e.g. `/allocations`.
"""


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
