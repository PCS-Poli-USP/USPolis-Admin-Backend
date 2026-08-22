"""Fetches live JupiterWeb pages for every code in
tests/data/jupiter/subject_codes.txt and writes an HTML+JSON snapshot.

Usage:
    poetry run python tests/scripts/generate_jupiter_snapshot.py
    poetry run python tests/scripts/generate_jupiter_snapshot.py --semester 2026.1
    poetry run python tests/scripts/generate_jupiter_snapshot.py --dest pending

Default `--dest snapshots` writes directly to tests/data/jupiter/snapshots/<semester>/
for a manual, deliberate regeneration (review the git diff before committing).
`--dest pending` writes to tests/data/jupiter/snapshots/pending/<semester>/ instead —
this is what the lazy staleness check in crawler_test_utils.py calls
programmatically; a human must then run promote_jupiter_snapshot.py.
"""

import argparse
import asyncio
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from server.db import engine  # noqa: F401  (imported for its side effect: registers models)
from tests.services.crawler_snapshot_utils import write_snapshot
from tests.services.jupiter_crawler.crawler_test_utils import (
    JUPITER_DATA_DIR,
    current_semester_label,
    fetch_snapshot_data,
    retrieve_subject_codes_to_test,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--semester",
        default=current_semester_label(),
        help="Semester label, e.g. 2026.1 (defaults to the current semester).",
    )
    parser.add_argument(
        "--dest",
        choices=["snapshots", "pending"],
        default="snapshots",
        help="Write directly to snapshots/<semester> (manual regen) or "
        "snapshots/pending/<semester> (unreviewed candidate).",
    )
    args = parser.parse_args()

    codes = retrieve_subject_codes_to_test()
    print(f"Fetching {len(codes)} subject codes for semester {args.semester}...")
    results = asyncio.run(fetch_snapshot_data(codes))
    print(f"Fetched {len(results)}/{len(codes)} successfully.")

    if args.dest == "pending":
        dest_dir = JUPITER_DATA_DIR / "snapshots" / "pending" / args.semester
    else:
        dest_dir = JUPITER_DATA_DIR / "snapshots" / args.semester

    write_snapshot(dest_dir, results, extra_manifest_fields={"semester": args.semester})
    print(f"Wrote snapshot to {dest_dir}")


if __name__ == "__main__":
    main()
