"""Shared file-IO helpers for the Jupiter/Janus crawler snapshot fixtures
(tests/data/{jupiter,janus}/). Each snapshot directory holds one HTML file
and one JSON reference file per subject code, plus a manifest.json recording
when it was generated and which codes it covers.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from server.models.database.subject_db_model import Subject


def read_subject_codes(path: Path) -> list[str]:
    """Read a subject-code list file, skipping blank lines and '#' comments."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def write_snapshot(
    dest_dir: Path,
    results: dict[str, tuple[bytes, Subject]],
    extra_manifest_fields: dict[str, object] | None = None,
) -> None:
    """Write html/<code>.html + references/<code>.json + manifest.json under dest_dir."""
    html_dir = dest_dir / "html"
    references_dir = dest_dir / "references"
    html_dir.mkdir(parents=True, exist_ok=True)
    references_dir.mkdir(parents=True, exist_ok=True)

    succeeded: list[str] = []
    for code, (html, subject) in results.items():
        (html_dir / f"{code}.html").write_bytes(html)
        (references_dir / f"{code}.json").write_text(
            subject.model_dump_json(), encoding="utf-8"
        )
        succeeded.append(code)

    manifest: dict[str, object] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "subject_codes": sorted(succeeded),
        **(extra_manifest_fields or {}),
    }
    (dest_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def snapshot_exists(dest_dir: Path) -> bool:
    return (dest_dir / "manifest.json").is_file()


def retrieve_html(dest_dir: Path, code: str) -> bytes:
    return (dest_dir / "html" / f"{code}.html").read_bytes()


def retrieve_reference(dest_dir: Path, code: str) -> dict:
    text = (dest_dir / "references" / f"{code}.json").read_text(encoding="utf-8")
    return json.loads(text)  # type: ignore[no-any-return]
