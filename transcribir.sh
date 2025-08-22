#!/bin/bash
# Script para transcribir audios con WhisperX

if [ -z "$1" ]; then
  echo "Uso: ./transcribir.sh ruta/al/audio.wav [idioma]"
  exit 1
fi

LANGUAGE=${2:-en}

# Ejecuta transcripción con la ruta exacta
AUDIO_PATH="$1"
BASENAME=$(basename "$AUDIO_PATH")
NAME="${BASENAME%.*}"

python scripts/transcribe.py "$AUDIO_PATH" --model small --language $LANGUAGE --batch_size 1 --compute_type float32

# Copia solo los archivos necesarios
mkdir -p docs/assets/audio
cp "data/transcripts/$NAME.json" docs/assets/audio/
cp "web/templates/transcript.html" "docs/$NAME.html"

# Reconstruir páginas
python scripts/build_pages.py
