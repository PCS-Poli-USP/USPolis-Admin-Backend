import pytest

from server.services.security.api_key_scope import (
    path_allowed,
    path_matches_prefix,
    validate_origin,
    validate_path_prefix,
)


class TestPathMatchesPrefix:
    @pytest.mark.parametrize(
        ("path", "prefix", "expected"),
        [
            ("/allocations", "/allocations", True),
            ("/allocations/events", "/allocations", True),
            ("/allocations/events/x", "/allocations/events", True),
            ("/allocationsx", "/allocations", False),
            ("/allocation", "/allocations", False),
            ("/classes", "/allocations", False),
            ("/anything/at/all", "/", True),
            ("/", "/", True),
        ],
    )
    def test_matches_whole_segments_only(
        self, path: str, prefix: str, expected: bool
    ) -> None:
        assert path_matches_prefix(path, prefix) is expected

    def test_any_of_several_prefixes(self) -> None:
        prefixes = ["/allocations", "/buildings"]

        assert path_allowed("/buildings", prefixes)
        assert path_allowed("/allocations/resources", prefixes)
        assert not path_allowed("/classes", prefixes)


class TestValidatePathPrefix:
    @pytest.mark.parametrize("prefix", ["/", "/allocations", "/allocations/events"])
    def test_accepts_clean_paths(self, prefix: str) -> None:
        assert validate_path_prefix(prefix) == prefix

    @pytest.mark.parametrize(
        "prefix",
        [
            "allocations",
            "/allocations/",
            "//allocations",
            "/allocations/../admin",
            "/./allocations",
            "/allocations?x=1",
            "/allocations*",
            "/alloc ations",
        ],
    )
    def test_rejects_unsafe_or_ambiguous_paths(self, prefix: str) -> None:
        with pytest.raises(ValueError):
            validate_path_prefix(prefix)


class TestValidateOrigin:
    @pytest.mark.parametrize(
        ("origin", "expected"),
        [
            ("https://gremio.poli.usp.br", "https://gremio.poli.usp.br"),
            ("https://Gremio.Poli.USP.br/", "https://gremio.poli.usp.br"),
            ("https://site.com:8443", "https://site.com:8443"),
        ],
    )
    def test_accepts_and_normalizes_https_origins(
        self, origin: str, expected: str
    ) -> None:
        assert validate_origin(origin, allow_insecure_localhost=False) == expected

    @pytest.mark.parametrize(
        "origin",
        [
            "http://gremio.poli.usp.br",
            "https://*.usp.br",
            "*",
            "https://site.com/path",
            "https://site.com?x=1",
            "https://user:pw@site.com",
            "gremio.poli.usp.br",
            "ftp://site.com",
        ],
    )
    def test_rejects_insecure_wildcard_or_non_origin_values(self, origin: str) -> None:
        with pytest.raises(ValueError):
            validate_origin(origin, allow_insecure_localhost=True)

    def test_http_localhost_only_when_allowed(self) -> None:
        assert (
            validate_origin("http://localhost:3000", allow_insecure_localhost=True)
            == "http://localhost:3000"
        )
        with pytest.raises(ValueError):
            validate_origin("http://localhost:3000", allow_insecure_localhost=False)
