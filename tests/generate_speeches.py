import json
from tts_modules.tts_tts import generate_audio_tts
from tts_modules.bark_tts import generate_audio_bark

# Nome del file JSON
JSON_FILE = "speeches.json"

MODEL = "TTS"  # TTS o BARK

# Carica i dati dal file JSON
try:
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        speeches = json.load(file)
except FileNotFoundError:
    print(f"❌ ERRORE: Il file {JSON_FILE} non esiste.")
    exit(1)

# Genera l'audio per ogni entry nel JSON
for entry in speeches:
    name = entry.get("name")
    text = entry.get("text")

    if not name or not text:
        print(f"⚠️ ERRORE: Dati mancanti in {entry}. Ignorato.")
        continue

    # Genera l'audio
    if MODEL == "TTS":
        generate_audio_tts(text, name)
    else:
        generate_audio_bark(text, name)
