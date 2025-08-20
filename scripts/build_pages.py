from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

TEMPLATE_PATH = Path("web/templates/transcript.html")
TRANSCRIPTS_DIR = Path("data/transcripts")
AUDIO_DIR = Path("data/audio")
PAGES_DIR = Path("web/pages")


def build_pages() -> None:
    """Generate an HTML page for each transcript JSON."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    for json_file in TRANSCRIPTS_DIR.glob("*.json"):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        title = data.get("title", json_file.stem)

        audio_file = next(AUDIO_DIR.glob(f"{json_file.stem}.*"), None)
        if audio_file is None:
            print(f"Skipping {json_file.name}: audio file not found")
            continue

        dest_audio = PAGES_DIR / audio_file.name
        shutil.copy(audio_file, dest_audio)

        audio_src = dest_audio.name
        json_src = os.path.relpath(json_file, PAGES_DIR)

        html = template.format(title=title, audio_src=audio_src, json_src=json_src)
        (PAGES_DIR / f"{json_file.stem}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_pages()
