from pathlib import Path

from tests.services.crawler_snapshot_utils import (
    read_subject_codes,
    retrieve_html,
    retrieve_reference,
)

JANUS_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "janus"
JANUS_SNAPSHOT_DIR = JANUS_DATA_DIR / "snapshots"


def retrieve_subject_codes_to_test() -> list[str]:
    return read_subject_codes(JANUS_DATA_DIR / "subject_codes.txt")


def retrieve_html_for_code(code: str) -> bytes:
    return retrieve_html(JANUS_SNAPSHOT_DIR, code)


def retrieve_reference_for_code(code: str) -> dict:
    return retrieve_reference(JANUS_SNAPSHOT_DIR, code)
