# Settings
from settings import TTS_MODEL

# Global Utils
from utils import capture_speech, play_audio, clean_text_for_tts

# TTS Modules
from tts_modules.tts_tts import generate_audio_tts
from tts_modules.bark_tts import generate_audio_bark

# Actions
from action_registry import ACTIONS


def execute_action(action_key, user_input):
    """
    Esegue tutti gli step definiti per una specifica azione.
    """
    action_steps = ACTIONS.get(action_key, {}).get("steps", [])
    context = {"user_input": user_input}

    for step in action_steps:
        function = step["function"]
        input_value = context.get(step["input_key"])
        if input_value is not None:
            output_value = function(input_value)
            context[step["output_key"]] = output_value

    return context.get("final_response", None)


def main():
    while True:
        text = capture_speech()
        if text:
            print(f"📜 Testo registrato: {text}")

            # Identifica l'azione richiesta dall'utente
            action_data = execute_action("GET_ACTION", text)
            action_key = action_data.get("action")

            if action_key and action_key in ACTIONS:
                print(f"🔹 Azione identificata: {action_key}")
                response = execute_action(action_key, text)

                if response:
                    print("📢 Risposta generata:")
                    print(response)

                    print("🔊 Pulizia testo per la generazione audio...")
                    response = clean_text_for_tts(response)

                    # Generazione audio
                    print("🔊 Generazione audio in corso...")
                    if TTS_MODEL == "TTS":
                        audio_file = generate_audio_tts(response, action_key)
                    else:
                        audio_file = generate_audio_bark(response, action_key)

                    print(f"🔊 Audio generato: {audio_file}")

                    # Riproduzione audio
                    play_audio(audio_file)
                else:
                    print("⚠️ Nessuna risposta generata.")
            else:
                print("⚠️ Azione non riconosciuta.")


if __name__ == "__main__":
    main()
