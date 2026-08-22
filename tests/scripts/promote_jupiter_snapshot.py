"""Promotes a reviewed pending Jupiter crawler snapshot to be the trusted
reference for its semester.

Usage:
    poetry run python tests/scripts/promote_jupiter_snapshot.py 2026.2

Review tests/data/jupiter/snapshots/pending/<semester>/ yourself first (e.g.
diff a few reference JSON files against the previous semester's, spot-check
the HTML) — this script does not inspect the content, it only moves it into
place. Refuses to overwrite an existing, already-promoted semester.
"""

import argparse
import shutil
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.services.jupiter_crawler.crawler_test_utils import JUPITER_DATA_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semester", help="Semester label to promote, e.g. 2026.2")
    args = parser.parse_args()

    pending_dir = JUPITER_DATA_DIR / "snapshots" / "pending" / args.semester
    dest_dir = JUPITER_DATA_DIR / "snapshots" / args.semester

    if not pending_dir.is_dir():
        raise SystemExit(f"No pending snapshot found at {pending_dir}")
    if dest_dir.exists():
        raise SystemExit(
            f"{dest_dir} already exists — refusing to overwrite an already-"
            "promoted snapshot. Remove it manually first if that's really "
            "what you want."
        )

    shutil.move(str(pending_dir), str(dest_dir))
    print(f"Promoted {pending_dir} -> {dest_dir}")


if __name__ == "__main__":
    main()
