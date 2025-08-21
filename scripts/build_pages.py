from __future__ import annotations

import json
import shutil
from pathlib import Path

TEMPLATE_PATH = Path("web/templates/transcript.html")
TRANSCRIPTS_DIR = Path("data/transcripts")
AUDIO_DIR = Path("data/audio")
DOCS_DIR = Path("docs")
ASSETS_DIR = DOCS_DIR / "assets"
CSS_SRC = Path("web/static/css/karaoke.css")
JS_SRC = Path("web/static/js/karaoke.js")


def build_pages() -> None:
    """Generate an HTML page for each transcript JSON and rebuild index."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    css_dir = ASSETS_DIR / "css"
    js_dir = ASSETS_DIR / "js"
    audio_dir = ASSETS_DIR / "audio"
    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy(CSS_SRC, css_dir / CSS_SRC.name)
    shutil.copy(JS_SRC, js_dir / JS_SRC.name)

    pages: list[tuple[str, str]] = []

    for json_file in sorted(TRANSCRIPTS_DIR.glob("*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        title = data.get("title", json_file.stem)

        audio_src = data.get("audio_url")
        if not audio_src:
            audio_file = next(AUDIO_DIR.glob(f"{json_file.stem}.*"), None)
            if audio_file is not None:
                audio_src = f"assets/audio/{audio_file.name}"
            else:
                audio_src = ""

        dest_json = audio_dir / json_file.name
        shutil.copy(json_file, dest_json)

        html = template.format(
            title=title,
            audio_src=audio_src,
            json_src=dest_json.name,
        )
        dest_html = DOCS_DIR / f"{json_file.stem}.html"
        dest_html.write_text(html, encoding="utf-8")
        pages.append((title, dest_html.name))
        print(f"Wrote {dest_html}")

    index_lines = [
        "<!DOCTYPE html>",
        "<html lang=\"es\">",
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <title>Transcripciones</title>",
        "</head>",
        "<body>",
        "  <h1>Transcripciones disponibles</h1>",
        "  <ul>",
    ]
    for title, filename in pages:
        index_lines.append(f'    <li><a href="{filename}">{title}</a></li>')
    index_lines += [
        "  </ul>",
        "</body>",
        "</html>",
    ]
    (DOCS_DIR / "index.html").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"Wrote {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    build_pages()
