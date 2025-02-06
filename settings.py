import os

# API
API_URL = "http://localhost:1234/v1/completions"

# TTS MODEL CONFIG
TTS_MODEL = "TTS"  # BARK | TTS
TTS_MODEL_NAME = "tts_models/it/mai_female/glow-tts"
MODEL_DIR = os.path.expanduser("~/.local/share/tts/")

# FILE STORAGE CONFIG
OVERWRITE = True
SPEECHES_DIR = "data/speeches"
