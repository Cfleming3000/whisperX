"""Transcribe audio files with WhisperX and export word-level timestamps.

Parameters
----------
audio : str
    Path to the input audio file to transcribe.
--model : str, optional
    Whisper model identifier to load, defaults to ``small``.
--language : str, optional
    Language code for the audio. If omitted, WhisperX will attempt to detect
    the spoken language automatically.
--device : str, optional
    Device for inference (``cuda`` or ``cpu``). Defaults to CUDA when
    available.
--batch_size : int, optional
    Batch size for model inference. Reduce if running out of GPU memory.
--compute_type : str, optional
    Precision for computation (``float16``, ``float32``, ``int8``). 
    Defaults to ``float32`` for maximum compatibility.

Output files are written to ``data/transcripts/`` using the audio file's base
name:

``data/transcripts/<name>.json``
    Full transcription result including per-word timings.
``data/transcripts/<name>.srt``
    Subtitle file with word-level highlight markup.
``data/transcripts/<name>.vtt``
    Subtitle file with word-level highlight markup.
``data/transcripts/<name>.txt``
    Plain text transcription without timestamps.
``data/transcripts/<name>_words.txt``
    Word-level transcription with timestamps.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
import whisperx
from whisperx.utils import get_writer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio with WhisperX and export JSON/SRT/VTT with word timings",
    )
    parser.add_argument("audio", type=str, help="Path to audio file to transcribe")
    parser.add_argument("--model", default="small", help="Whisper model name to use")
    parser.add_argument(
        "--language",
        default=None,
        help="Language code for the audio; if omitted, language will be detected",
    )
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Inference device",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=8,
        help="Batch size for inference",
    )
    parser.add_argument(
        "--compute_type",
        default="float32",
        help="Precision for computation (float16, float32, int8). Default: float32",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    audio_path = Path(args.audio)
    output_dir = Path("data/transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load audio
    audio = whisperx.load_audio(str(audio_path))

    # Load model
    model = whisperx.load_model(
        args.model,
        args.device,
        language=args.language,
        compute_type=args.compute_type,
    )

    # Transcribe
    result = model.transcribe(audio, batch_size=args.batch_size)

    # Detect language safely (from result or args)
    lang = result.get("language", args.language or "en")

    # Align to retrieve word-level timestamps
    align_model, metadata = whisperx.load_align_model(
        language_code=lang, device=args.device
    )
    result = whisperx.align(result["segments"], align_model, metadata, audio, args.device)

    # Ensure "language" key exists for compatibility with writers
    if "language" not in result:
        result["language"] = lang

    # Export JSON, SRT, VTT
    writer_args = {
        "highlight_words": True,
        "max_line_width": None,
        "max_line_count": None,
    }

    for fmt in ("json", "srt", "vtt"):
        writer = get_writer(fmt, str(output_dir))
        writer(result, str(audio_path), writer_args)

    # Extra: export plain TXT (just text)
    txt_path = output_dir / f"{audio_path.stem}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            f.write(seg["text"].strip() + "\n")

    # Extra: export TXT with word-level timestamps
    words_path = output_dir / f"{audio_path.stem}_words.txt"
    with open(words_path, "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            if "words" in seg:
                for w in seg["words"]:
                    f.write(f"[{w['start']:.2f} - {w['end']:.2f}] {w['word']}\n")


if __name__ == "__main__":
    main()
