# Constants
from data.constants.items import LOL_ITEMS

# Settings
from settings import TTS_MODEL

# Global Utils
from utils import capture_speech, play_audio

# TTS Modules
from tts_modules.tts_tts import generate_audio_tts
from tts_modules.bark_tts import generate_audio_bark

# Actions
from actions.get_lol_items import llm_get_item, generate_description
from actions.generic_questions import llm_generic_question
from actions.get_action import llm_get_action


# Funzione principale
def main():
    test = llm_get_action("quando è terminata la seconda guerra mondiale?")

    print(test)
    # while True:
    #     text = capture_speech()
    #     if text:
    #         print(f"📜 Testo registrato: {text}")
    #         item_data = llm_get_item(text)
    #         item_key = item_data.get("item")

    #         if item_key:
    #             print(f"🔹 Item identificato: {item_key}")
    #             if item_key in LOL_ITEMS:
    #                 description = generate_description(item_key)
    #                 print("📢 Descrizione generata:")
    #                 print(description)

    #                 # Generazione audio
    #                 print("🔊 Generazione audio in corso...")

    #                 if TTS_MODEL == "TTS":
    #                     audio_file = generate_audio_tts(description, item_key)
    #                 else:
    #                     audio_file = generate_audio_bark(description, item_key)

    #                 print(f"🔊 Audio generato: {audio_file}")

    #                 # Riproduzione audio
    #                 play_audio(audio_file)
    #             else:
    #                 print("⚠️ Oggetto non riconosciuto.")


if __name__ == "__main__":
    main()
