#!/bin/bash
# Script para limpiar transcripciones generadas por WhisperX
# Uso: ./limpiar.sh nombre_base
# Ejemplo: ./limpiar.sh audio   --> elimina audio.json, audio.srt, etc.

if [ -z "$1" ]; then
  echo "Uso: ./limpiar.sh nombre_base"
  exit 1
fi

BASENAME=$1

# Archivos en data/transcripts
rm -f data/transcripts/${BASENAME}.json
rm -f data/transcripts/${BASENAME}.srt
rm -f data/transcripts/${BASENAME}.txt
rm -f data/transcripts/${BASENAME}.vtt
rm -f data/transcripts/${BASENAME}_words.txt

# Archivos en docs/assets/audio
rm -f docs/assets/audio/${BASENAME}.json
rm -f docs/assets/audio/${BASENAME}.mp3

# Archivos HTML en docs
rm -f docs/${BASENAME}.html

# Confirmación
echo "✅ Limpieza completa para: $BASENAME"

# Git commit & push automático
git add .
git commit -m "Cleanup: eliminar transcripción $BASENAME y archivos generados"
git push origin main

echo "📤 Cambios subidos al repositorio con éxito"
