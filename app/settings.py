import os

# API
API_URL = "http://localhost:1234/v1/completions"

# TTS MODEL CONFIG
TTS_MODEL = "TTS"  # BARK | TTS
TTS_MODEL_NAME = "tts_models/it/mai_female/glow-tts"
MODEL_DIR = os.path.expanduser("~/.local/share/tts/")

# TTS COMMAND
TTS_OPEN_REC = "computer attivati"
TTS_CLOSE_REC = "computer elabora"
TTS_UNDO_REC = "computer stop"

# FILE STORAGE CONFIG
OVERWRITE = True
SPEECHES_DIR = "data/speeches"

# LLM MODELS
GEMMA = "gemma-2-2b-instruct"
QWEN = "qwen2.5-coder-7b-instruct"
DEEP_SEEK_LLAMA = "deepseek-r1-distill-llama-8b"
