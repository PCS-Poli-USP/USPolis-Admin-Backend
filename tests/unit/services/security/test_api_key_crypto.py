import re

import pytest

from server.services.security.api_key_crypto import (
    API_KEY_PATTERN,
    BASE62_ALPHABET,
    CURRENT_HASH_VERSION,
    ApiKeyEnv,
    ApiKeySecretNotConfigured,
    current_env,
    generate_api_key,
    hash_api_key,
    parse_api_key,
    verify_api_key,
)

SECRET_FIELD = re.compile(r"^[0-9A-Za-z]{43}$")


def swap_char(text: str, index: int, alphabet: str) -> str:
    """`text` with the character at `index` replaced by a different one
    from `alphabet`."""
    replacement = next(char for char in alphabet if char != text[index])
    return text[:index] + replacement + text[index + 1 :]


class TestFormat:
    @pytest.mark.parametrize("env", list(ApiKeyEnv))
    def test_matches_the_published_scanner_pattern(self, env: ApiKeyEnv) -> None:
        plaintext = generate_api_key(env).plaintext

        assert API_KEY_PATTERN.fullmatch(plaintext)
        assert plaintext.startswith(f"up_{env}_")

    def test_has_five_underscore_separated_fields(self) -> None:
        generated = generate_api_key(ApiKeyEnv.LIVE)
        prefix, env, public_id, secret, checksum = generated.plaintext.split("_")

        assert (prefix, env) == ("up", "live")
        assert public_id == generated.public_id and len(public_id) == 16
        assert SECRET_FIELD.match(secret)
        assert len(checksum) == 6 and set(checksum) <= set(BASE62_ALPHABET)

    def test_keys_are_unique(self) -> None:
        keys = {generate_api_key(ApiKeyEnv.DEV).plaintext for _ in range(200)}

        assert len(keys) == 200

    def test_scanner_pattern_finds_keys_inside_other_text(self) -> None:
        plaintext = generate_api_key(ApiKeyEnv.LIVE).plaintext
        leaked = f'API_TOKEN="{plaintext}" # do not commit'

        match = API_KEY_PATTERN.search(leaked)
        assert match is not None and match.group(0) == plaintext


class TestParse:
    def test_valid_key_returns_its_public_id(self) -> None:
        generated = generate_api_key(ApiKeyEnv.LIVE)

        assert parse_api_key(generated.plaintext, ApiKeyEnv.LIVE) == generated.public_id

    def test_key_from_another_environment_is_rejected(self) -> None:
        staging_key = generate_api_key(ApiKeyEnv.TEST).plaintext

        assert parse_api_key(staging_key, ApiKeyEnv.LIVE) is None

    @pytest.mark.parametrize(
        ("field_index", "alphabet"),
        [(2, "0123456789abcdef"), (3, BASE62_ALPHABET)],
        ids=["typo-in-public-id", "typo-in-secret"],
    )
    def test_one_character_typo_is_caught_by_the_checksum(
        self, field_index: int, alphabet: str
    ) -> None:
        fields = generate_api_key(ApiKeyEnv.LIVE).plaintext.split("_")
        # Stay inside the field's alphabet so the shape is still valid and
        # only the checksum can reject the key.
        fields[field_index] = swap_char(fields[field_index], 5, alphabet)

        assert parse_api_key("_".join(fields), ApiKeyEnv.LIVE) is None

    @pytest.mark.parametrize(
        "plaintext",
        [
            "",
            "up_live_short",
            "sk_live_0123456789abcdef_" + "a" * 43 + "_aaaaaa",
            "up_prod_0123456789abcdef_" + "a" * 43 + "_aaaaaa",
            "up_live_0123456789ABCDEF_" + "a" * 43 + "_aaaaaa",
            "up_live_0123456789abcdef_" + "a" * 42 + "-_aaaaaa",
        ],
        ids=[
            "empty",
            "truncated",
            "other-prefix",
            "unknown-env",
            "upper-hex",
            "bad-char",
        ],
    )
    def test_malformed_keys_are_rejected(self, plaintext: str) -> None:
        assert parse_api_key(plaintext, ApiKeyEnv.LIVE) is None

    def test_defaults_to_the_server_environment(self) -> None:
        generated = generate_api_key()

        assert generated.plaintext.startswith(f"up_{current_env()}_")
        assert parse_api_key(generated.plaintext) == generated.public_id


class TestHash:
    def test_hash_round_trips_and_is_not_the_plaintext(self) -> None:
        generated = generate_api_key(ApiKeyEnv.LIVE)

        assert generated.key_hash != generated.plaintext
        assert len(generated.key_hash) == 64
        assert generated.hash_version == CURRENT_HASH_VERSION
        assert verify_api_key(
            generated.plaintext, generated.key_hash, generated.hash_version
        )

    def test_a_different_key_does_not_verify(self) -> None:
        first = generate_api_key(ApiKeyEnv.LIVE)
        second = generate_api_key(ApiKeyEnv.LIVE)

        assert not verify_api_key(second.plaintext, first.key_hash, first.hash_version)

    def test_hash_depends_on_the_server_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        plaintext = generate_api_key(ApiKeyEnv.LIVE).plaintext
        original = hash_api_key(plaintext)
        monkeypatch.setattr(
            "server.services.security.api_key_crypto.CONFIG.api_key_secret",
            "another-secret-that-is-long-enough-0123",
        )

        assert hash_api_key(plaintext) != original

    @pytest.mark.parametrize("secret", ["", "too-short"])
    def test_missing_or_short_secret_raises(
        self, monkeypatch: pytest.MonkeyPatch, secret: str
    ) -> None:
        monkeypatch.setattr(
            "server.services.security.api_key_crypto.CONFIG.api_key_secret", secret
        )

        with pytest.raises(ApiKeySecretNotConfigured):
            generate_api_key(ApiKeyEnv.LIVE)

    def test_unknown_hash_version_raises(self) -> None:
        with pytest.raises(ValueError, match="hash version"):
            hash_api_key("anything", version=99)


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ("production", ApiKeyEnv.LIVE),
        ("PRODUCTION", ApiKeyEnv.LIVE),
        ("staging", ApiKeyEnv.TEST),
        ("development", ApiKeyEnv.DEV),
        ("DEVELOPMENT", ApiKeyEnv.DEV),
    ],
)
def test_current_env_follows_the_environment(
    monkeypatch: pytest.MonkeyPatch, environment: str, expected: ApiKeyEnv
) -> None:
    monkeypatch.setattr(
        "server.services.security.api_key_crypto.CONFIG.environment", environment
    )

    assert current_env() == expected
