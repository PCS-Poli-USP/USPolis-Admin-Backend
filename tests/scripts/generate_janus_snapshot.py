"""Fetches live Janus pages for every code in
tests/data/janus/subject_codes.txt and writes an HTML+JSON snapshot to
tests/data/janus/snapshots/.

Usage:
    poetry run python tests/scripts/generate_janus_snapshot.py

Unlike Jupiter, Janus (postgraduate offerings) isn't semester-scoped, so
this always writes directly to snapshots/ — there's no pending/promote
step. Review the resulting git diff yourself before committing, same as
any other fixture data change.
"""

import asyncio
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from httpx import AsyncClient

from server.db import engine  # noqa: F401  (imported for its side effect: registers models)
from server.services.janus_crawler.crawler import JanusCrawler
from tests.services.crawler_snapshot_utils import write_snapshot
from tests.services.janus_crawler.crawler_test_utils import (
    JANUS_SNAPSHOT_DIR,
    retrieve_subject_codes_to_test,
)

# Mirrors JanusCrawler's private __get_subject_ofe lookup
# (server/services/janus_crawler/crawler.py) — needed here because we want
# the HTML for a specific, known offering to snapshot, and JanusCrawler
# doesn't expose ofe resolution publicly; crawl_subject_static only resolves
# it internally as part of a full live fetch, which we're deliberately
# splitting into two steps (resolve, then fetch+save) here.
_OFE_URL = "https://uspdigital.usp.br/janus/DisciplinaAux"
_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}


async def _resolve_ofe(subject_code: str) -> str | None:
    async with AsyncClient() as client:
        response = await client.post(
            _OFE_URL,
            params={"tipo": "T"},
            headers=_HEADERS,
            data={"sgldis": subject_code, "nomdis": ""},
        )
        for item in response.text.split('"'):
            if f"publico/turma/{subject_code}/" in item:
                return item.split("/")[-1]
        return None


async def fetch_all(codes: list[str]) -> dict:
    results = {}
    for code in codes:
        ofe = await _resolve_ofe(code)
        if ofe is None:
            print(f"Error processing {code}: no active offering (ofe) found")
            continue
        crawler = JanusCrawler(code)
        try:
            html = await crawler.request_html(ofe)
            subject = await JanusCrawler.crawl_subject_static(code, page_content=html)
        except Exception as e:  # noqa: BLE001
            print(f"Error processing {code}: {e}")
            continue
        results[code] = (html, subject)
    return results


def main() -> None:
    codes = retrieve_subject_codes_to_test()
    print(f"Fetching {len(codes)} Janus subject codes...")
    results = asyncio.run(fetch_all(codes))
    print(f"Fetched {len(results)}/{len(codes)} successfully.")
    write_snapshot(JANUS_SNAPSHOT_DIR, results)
    print(f"Wrote snapshot to {JANUS_SNAPSHOT_DIR}")


if __name__ == "__main__":
    main()
