# FastChain
from fastchain.core import Action

# TTS Modules
from app.actions.core.text_to_audio.tts_modules.tts_tts import generate_audio_tts
from app.actions.core.text_to_audio.tts_modules.bark_tts import generate_audio_bark

# Utils
from app.utils import clean_text_for_tts

# Settings
from settings import TTS_MODEL


class TextToAudioAction:
    """
    Classe che, dato un testo, lo pulisce e genera un file audio utilizzando il modello configurato.
    """

    def execute(self, text: str) -> str:
        """Genera un file audio dal testo dato."""
        if not text:
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


TEXT_TO_AUDIO = Action(
    name="TEXT_TO_AUDIO",
    description="Pulisce un testo e lo converte in un file audio.",
    verbose_name="Testo in Audio",
    core=True,
    steps=[
        {
            "function": TextToAudioAction().execute,
            "input_type": str,
            "output_type": str,
            "thread": True,
        }
    ],
    input_action=False,
)
