import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from server.config import CONFIG
from server.services.email.email_service import env, template_path

# Links to pages of an environment's own site must come from FRONTEND_URL,
# never a hard-coded domain: see the frontend_url global in email_service.py.
_HARD_CODED_SITE_LINK = re.compile(r'href="https?://(www\.)?uspolis\.com\.br', re.I)


def test_the_frontend_url_global_is_the_configured_frontend() -> None:
    assert env.globals["frontend_url"] == CONFIG.frontend_url.rstrip("/")


@pytest.mark.parametrize(
    ("template", "path"),
    [
        ("/reports/bug-report.html", "/admin/bug-reports"),
        ("/solicitations/solicitation-requested.html", "/scheduling/solicitations"),
    ],
)
def test_page_links_point_at_the_frontend_url(template: str, path: str) -> None:
    with patch.dict(env.globals, {"frontend_url": "https://front.example"}):
        body = env.get_template(template).render(data=SimpleNamespace())

    assert f'href="https://front.example{path}"' in body


@pytest.mark.parametrize(
    "template_file",
    sorted(Path(template_path).rglob("*.html")),
    ids=lambda p: str(p.relative_to(template_path)),
)
def test_no_template_hard_codes_the_site_domain(template_file: Path) -> None:
    assert not _HARD_CODED_SITE_LINK.search(template_file.read_text())
