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

Output files are written to ``data/transcripts/`` using the audio file's base
name:

``data/transcripts/<name>.json``
    Full transcription result including per-word timings.
``data/transcripts/<name>.srt``
    Subtitle file with word-level highlight markup.
``data/transcripts/<name>.vtt``
    Subtitle file with word-level highlight markup.
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    audio_path = Path(args.audio)
    output_dir = Path("data/transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    audio = whisperx.load_audio(str(audio_path))
    model = whisperx.load_model(args.model, args.device, language=args.language)
    result = model.transcribe(audio, batch_size=args.batch_size)

    # Align to retrieve word-level timestamps
    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"], device=args.device
    )
    result = whisperx.align(result["segments"], align_model, metadata, audio, args.device)

    writer_args = {"highlight_words": True}
    for fmt in ("json", "srt", "vtt"):
        writer = get_writer(fmt, str(output_dir))
        writer(result, str(audio_path), writer_args)


if __name__ == "__main__":
    main()
