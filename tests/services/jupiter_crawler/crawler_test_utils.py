import asyncio
from pathlib import Path

from server.models.database.subject_db_model import Subject
from server.services.jupiter_crawler.crawler import JupiterCrawler
from server.utils.brazil_datetime import BrazilDatetime
from tests.services.crawler_snapshot_utils import (
    read_subject_codes,
    retrieve_html,
    retrieve_reference,
    snapshot_exists,
    write_snapshot,
)

JUPITER_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "jupiter"


def current_semester_label() -> str:
    now = BrazilDatetime.now_utc()
    semester = 1 if now.month <= 6 else 2
    return f"{now.year}.{semester}"


def retrieve_subject_codes_to_test() -> list[str]:
    return read_subject_codes(JUPITER_DATA_DIR / "subject_codes.txt")


async def fetch_snapshot_data(codes: list[str]) -> dict[str, tuple[bytes, Subject]]:
    """Live-fetch HTML + parsed Subject for each code. Used by both the
    manual generate script (tests/scripts/generate_jupiter_snapshot.py) and
    the lazy pending-snapshot fetch below."""
    results: dict[str, tuple[bytes, Subject]] = {}
    for code in codes:
        crawler = JupiterCrawler(code)
        try:
            html = await crawler.request_html()
            subject = await JupiterCrawler.crawl_subject_static(code, page_content=html)
        except Exception as e:  # noqa: BLE001
            print(f"Error processing {code}: {e}")
            continue
        results[code] = (html, subject)
    return results


def ensure_fresh_snapshot() -> str:
    """Return the semester label whose snapshot should be tested against.

    If the current semester has no reviewed snapshot yet, this lazily makes
    one live under snapshots/pending/<semester>/ and raises — a human must
    review it and run promote_jupiter_snapshot.py before tests can pass
    again. This never silently trusts freshly-scraped data as correct,
    since a real JupiterWeb structure change that breaks parsing must not
    silently become the new "reference"."""
    label = current_semester_label()
    snapshots_dir = JUPITER_DATA_DIR / "snapshots" / label
    if snapshot_exists(snapshots_dir):
        return label

    pending_dir = JUPITER_DATA_DIR / "snapshots" / "pending" / label
    if snapshot_exists(pending_dir):
        raise RuntimeError(
            f"No reviewed Jupiter crawler snapshot for semester {label} yet, "
            f"but a pending candidate already exists at {pending_dir}. Review "
            "it (e.g. diff the reference JSON files against the previous "
            "semester's) and run: poetry run python "
            f"tests/scripts/promote_jupiter_snapshot.py {label}"
        )

    print(
        f"No Jupiter crawler snapshot for semester {label} — fetching a "
        "candidate now (saved as pending, not trusted automatically)..."
    )
    codes = retrieve_subject_codes_to_test()
    try:
        results = asyncio.run(fetch_snapshot_data(codes))
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            f"No snapshot for semester {label}, and the live fetch to create "
            f"a pending candidate failed ({e}). Run manually: poetry run "
            f"python tests/scripts/generate_jupiter_snapshot.py --semester "
            f"{label} --dest pending (requires network access)."
        ) from e

    write_snapshot(pending_dir, results, extra_manifest_fields={"semester": label})
    raise RuntimeError(
        f"No reviewed Jupiter crawler snapshot for semester {label} — a fresh "
        f"candidate was just fetched and saved to {pending_dir}. Review it "
        f"and run: poetry run python tests/scripts/promote_jupiter_snapshot.py "
        f"{label}"
    )


def retrieve_html_for_semester(code: str, semester: str) -> bytes:
    return retrieve_html(JUPITER_DATA_DIR / "snapshots" / semester, code)


def retrieve_reference_for_semester(code: str, semester: str) -> dict:
    return retrieve_reference(JUPITER_DATA_DIR / "snapshots" / semester, code)
