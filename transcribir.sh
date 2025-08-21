#!/bin/bash
# Script para transcribir audios con WhisperX

# Verifica que se pasó un archivo
if [ -z "$1" ]; then
  echo "Uso: ./transcribir.sh nombre_del_audio.wav [idioma]"
  exit 1
fi

# Si no se pasa idioma, por defecto "en"
LANGUAGE=${2:-en}

# Ejecuta el comando de transcripción
python scripts/transcribe.py "data/audio/$1" --model small --language $LANGUAGE --batch_size 1 --compute_type float32

# Copia solo los archivos necesarios para GitHub Pages
BASENAME="${1%.*}"
mkdir -p docs/assets/audio
cp "data/transcripts/$BASENAME.json" docs/assets/audio/
cp "web/templates/transcript.html" "docs/$BASENAME.html"

# Rebuild HTML pages for GitHub Pages
python scripts/build_pages.py
