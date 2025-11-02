from enum import Enum


class AudiovisualType(str, Enum):
    TV = "tv"
    PROJECTOR = "projector"
    NONE = "none"

    @classmethod
    def from_str(cls, value: str) -> "AudiovisualType":
        tv_values = ["TV"]
        projector_values = ["Projetor"]
        none_values = ["Nenhum"]

        if value in tv_values:
            return cls.TV
        if value in projector_values:
            return cls.PROJECTOR
        if value in none_values:
            return cls.NONE
        raise NoSuchAudiovisualType(f"Audiovisual {value} is not valid.")

    @staticmethod
    def values() -> list["AudiovisualType"]:
        return [
            AudiovisualType.TV,
            AudiovisualType.PROJECTOR,
            AudiovisualType.NONE,
        ]


class NoSuchAudiovisualType(Exception):
    pass
