import pytest

from server.services.security.api_key_scope import (
    path_allowed,
    path_matches_prefix,
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
