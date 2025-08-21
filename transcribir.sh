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
