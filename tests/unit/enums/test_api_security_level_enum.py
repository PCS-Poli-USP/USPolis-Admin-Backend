import pytest

from server.utils.enums.api_security_level_enum import APISecurityLevel


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        (["Admin"], APISecurityLevel.ADMIN),
        (["Restricted"], APISecurityLevel.RESTRICTED),
        (["Authenticated"], APISecurityLevel.AUTHENTICATED),
        (["Public"], APISecurityLevel.PUBLIC),
        ([], APISecurityLevel.UNKNOWN),
        (["Something Else"], APISecurityLevel.UNKNOWN),
    ],
)
def test_get_from_tags_maps_known_tags(
    tags: list[str], expected: APISecurityLevel
) -> None:
    assert APISecurityLevel.get_from_tags(tags) == expected


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        (["Admin", "Restricted"], APISecurityLevel.ADMIN),
        (["Restricted", "Authenticated"], APISecurityLevel.RESTRICTED),
        (["Authenticated", "Public"], APISecurityLevel.AUTHENTICATED),
        (["Admin", "Restricted", "Authenticated", "Public"], APISecurityLevel.ADMIN),
    ],
)
def test_get_from_tags_prioritizes_the_most_privileged_tag(
    tags: list[str], expected: APISecurityLevel
) -> None:
    assert APISecurityLevel.get_from_tags(tags) == expected
