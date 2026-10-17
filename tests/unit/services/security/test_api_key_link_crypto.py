import pytest

from server.services.security.api_key_link_crypto import (
    NONCE_BYTES,
    SALT_BYTES,
    SealedApiKey,
    generate_link_id,
    open_sealed_api_key,
    seal_api_key,
)

PLAINTEXT = "up_dev_a1b2c3d4e5f60718_" + "x" * 43 + "_abcdef"


@pytest.fixture
def link_id() -> str:
    return generate_link_id()


@pytest.fixture
def sealed(link_id: str) -> SealedApiKey:
    return seal_api_key(PLAINTEXT, link_id)


def open_with(sealed: SealedApiKey, link_id: str, **overrides: object) -> str | None:
    args: dict[str, object] = {
        "token": sealed.token,
        "link_id": link_id,
        "ciphertext": sealed.ciphertext,
        "nonce": sealed.nonce,
        "salt": sealed.salt,
        **overrides,
    }
    return open_sealed_api_key(**args)  # type: ignore[arg-type]


class TestSeal:
    def test_round_trips_with_the_right_token(
        self, sealed: SealedApiKey, link_id: str
    ) -> None:
        assert open_with(sealed, link_id) == PLAINTEXT

    def test_ciphertext_does_not_contain_the_key(self, sealed: SealedApiKey) -> None:
        assert PLAINTEXT.encode() not in sealed.ciphertext
        assert b"x" * 43 not in sealed.ciphertext

    def test_token_is_url_safe_and_256_bits(self, sealed: SealedApiKey) -> None:
        # token_urlsafe(32): 32 bytes as unpadded base64url = 43 chars.
        assert len(sealed.token) == 43
        assert all(c.isalnum() or c in "-_" for c in sealed.token)

    def test_every_seal_is_fresh(self, link_id: str) -> None:
        first = seal_api_key(PLAINTEXT, link_id)
        second = seal_api_key(PLAINTEXT, link_id)

        assert first.token != second.token
        assert first.salt != second.salt
        assert first.nonce != second.nonce
        assert first.ciphertext != second.ciphertext
        assert len(first.nonce) == NONCE_BYTES
        assert len(first.salt) == SALT_BYTES

    def test_link_ids_are_16_hex_chars(self) -> None:
        link_id = generate_link_id()
        assert len(link_id) == 16
        int(link_id, 16)


class TestOpenRejects:
    def test_a_wrong_token(self, sealed: SealedApiKey, link_id: str) -> None:
        other = seal_api_key(PLAINTEXT, link_id).token
        assert open_with(sealed, link_id, token=other) is None

    def test_another_links_id(self, sealed: SealedApiKey) -> None:
        """link_id is the associated data: a ciphertext moved to another
        row can't be opened there."""
        assert open_with(sealed, generate_link_id()) is None

    def test_a_tampered_ciphertext(self, sealed: SealedApiKey, link_id: str) -> None:
        tampered = bytes([sealed.ciphertext[0] ^ 1]) + sealed.ciphertext[1:]
        assert open_with(sealed, link_id, ciphertext=tampered) is None

    def test_a_different_salt(self, sealed: SealedApiKey, link_id: str) -> None:
        assert open_with(sealed, link_id, salt=b"\x00" * SALT_BYTES) is None

    def test_a_different_nonce(self, sealed: SealedApiKey, link_id: str) -> None:
        assert open_with(sealed, link_id, nonce=b"\x00" * NONCE_BYTES) is None
