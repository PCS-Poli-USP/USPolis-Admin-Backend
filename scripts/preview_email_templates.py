"""Render every email template with sample data so they can be eyeballed in a browser.

Usage:
    poetry run python scripts/preview_email_templates.py

Writes static HTML files (with an index.html linking to all of them) to
`email_previews/` at the repo root, then prints the path to open.
"""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "server" / "templates"
OUTPUT_DIR = REPO_ROOT / "email_previews"
LOGO_ASSET = REPO_ROOT / "server" / "static" / "assets" / "uspolis-logo-email.png"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
# Real emails point logo_url at a hosted URL (see email_service.py); for a local,
# offline-friendly preview we copy the asset alongside the output and link to it
# relatively instead.
env.globals["logo_url"] = "assets/uspolis-logo-email.png"

SAMPLE_DATA: dict[str, tuple[str, dict[str, object]]] = {
    "solicitation-requested": (
        "/solicitations/solicitation-requested.html",
        {
            "requester": "Maria Oliveira",
            "requester_email": "maria.oliveira@usp.br",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "building": "Escola Politécnica - Bloco A",
            "classroom": "Sala 12",
            "time": "08:00 ~ 10:00",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
            "capacity": 60,
            "reason": "Aplicação de prova substitutiva para alunos da turma noturna.",
        },
    ),
    "solicitation-approved": (
        "/solicitations/solicitation-approved.html",
        {
            "username": "Maria Oliveira",
            "building": "Escola Politécnica - Bloco A",
            "approved_classroom": "Sala 14",
            "time": "08:00 ~ 10:00",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "classroom": "Sala 12",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
            "capacity": 60,
        },
    ),
    "solicitation-updated": (
        "/solicitations/solicitation-updated.html",
        {
            "username": "Maria Oliveira",
            "building": "Escola Politécnica - Bloco B",
            "approved_classroom": "Sala 21",
            "time": "10:00 ~ 12:00",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "classroom": "Sala 12",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
            "capacity": 60,
        },
    ),
    "solicitation-denied": (
        "/solicitations/solicitation-denied.html",
        {
            "username": "Maria Oliveira",
            "justification": "Sala já reservada para manutenção elétrica programada neste período.",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "building": "Escola Politécnica - Bloco A",
            "classroom": "Sala 12",
            "time": "08:00 ~ 10:00",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
            "capacity": 60,
        },
    ),
    "solicitation-cancelled": (
        "/solicitations/solicitation-cancelled.html",
        {
            "requester": "Maria Oliveira",
            "requester_email": "maria.oliveira@usp.br",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "building": "Escola Politécnica - Bloco A",
            "classroom": "Sala 12",
            "time": "08:00 ~ 10:00",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
            "capacity": 60,
            "reason": "Prova remarcada para outra data.",
        },
    ),
    "solicitation-deleted": (
        "/solicitations/solicitation-deleted.html",
        {
            "username": "Maria Oliveira",
            "title": "Prova de Cálculo I",
            "type": "Prova",
            "building": "Escola Politécnica - Bloco A",
            "classroom": "Sala 12",
            "time": "08:00 ~ 10:00",
            "dates": "12/08/2026, 19/08/2026, 26/08/2026",
        },
    ),
    "feedback": (
        "/feedbacks/feedback.html",
        {
            "user_name": "João Pereira",
            "user_email": "joao.pereira@usp.br",
            "title": "Sugestão de melhoria no calendário",
            "message": "Seria ótimo poder filtrar as reservas por prédio diretamente no calendário principal.",
        },
    ),
    "bug-report": (
        "/reports/bug-report.html",
        {
            "user_name": "João Pereira",
            "user_email": "joao.pereira@usp.br",
            "type": "Interface",
            "priority": "Alta",
            "description": "Ao aprovar uma solicitação pelo celular, o botão de confirmação fica fora da tela.",
        },
    ),
}


def render_all() -> list[tuple[str, Path]]:
    OUTPUT_DIR.mkdir(exist_ok=True)
    assets_dir = OUTPUT_DIR / "assets"
    assets_dir.mkdir(exist_ok=True)
    shutil.copy(LOGO_ASSET, assets_dir / LOGO_ASSET.name)
    rendered = []
    for name, (template_name, data) in SAMPLE_DATA.items():
        template = env.get_template(template_name)
        html = template.render(data=data)
        out_path = OUTPUT_DIR / f"{name}.html"
        out_path.write_text(html, encoding="utf-8")
        rendered.append((name, out_path))
    return rendered


def write_index(rendered: list[tuple[str, Path]]) -> Path:
    links = "\n".join(
        f'<li><a href="{path.name}">{name}</a></li>' for name, path in rendered
    )
    index_html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>USPolis - Preview de templates de email</title>
<style>
    body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 480px; margin: 60px auto; color: #22302f; }}
    h1 {{ color: #408080; }}
    li {{ margin-bottom: 8px; font-size: 15px; }}
    a {{ color: #2f6666; }}
</style>
</head>
<body>
<h1>Preview de templates de email</h1>
<ul>
{links}
</ul>
</body>
</html>
"""
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    return index_path


if __name__ == "__main__":
    rendered = render_all()
    index_path = write_index(rendered)
    print(f"Rendered {len(rendered)} templates to {OUTPUT_DIR}/")
    print(f"Open in your browser: {index_path}")
    print(
        f"Or serve it: cd {OUTPUT_DIR} && python3 -m http.server 8000  (then visit http://localhost:8000)"
    )
