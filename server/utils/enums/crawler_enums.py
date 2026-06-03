from enum import Enum


class CrawlerType(str, Enum):
    JUPITER = "jupiter"
    JANUS = "janus"


class CrawlerStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
