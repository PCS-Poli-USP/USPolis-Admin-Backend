import pytest

from server.utils.enums.audiovisual_type_enum import (
    AudiovisualType,
    NoSuchAudiovisualType,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("TV", AudiovisualType.TV),
        ("Projetor", AudiovisualType.PROJECTOR),
        ("Nenhum", AudiovisualType.NONE),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: AudiovisualType) -> None:
    assert AudiovisualType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchAudiovisualType):
        AudiovisualType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(AudiovisualType.values()) == set(AudiovisualType)
