import os

# TTS Modules
from tts_modules.tts_tts import generate_audio_tts
from tts_modules.bark_tts import generate_audio_bark

# Utils
from utils import clean_text_for_tts

# Settings
from settings import TTS_MODEL


def generate_audio(text):
    """Genera un file audio dal testo dato utilizzando il modello configurato."""
    if not text:  # 🔹 Se il testo è None o vuoto, assegna un valore di default
        print("Nessun testo riconosciuto! Non posso generare l'audio.")
        return None

    print("🔊 Pulizia testo per la generazione audio...")
    cleaned_text = clean_text_for_tts(text)

    print("🔊 Generazione audio in corso...")
    if TTS_MODEL == "TTS":
        audio_file = generate_audio_tts(cleaned_text, "tmp_audio")
    else:
        audio_file = generate_audio_bark(cleaned_text, "tmp_audio")

    print(f"🔊 Audio generato: {audio_file}")
    return audio_file


ACTION_CHAIN = {
    "metadata": {
        "name": "TEXT_TO_AUDIO",
        "description": "Pulisce un testo e lo converte in un file audio.",
        "verbose_name": "Testo in Audio",
        "input_action": False,
    },
    "steps": [
        {
            "function": "generate_audio",
            "input_key": "user_input",
            "output_key": "final_response",
        }
    ],
}
