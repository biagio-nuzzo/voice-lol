# Built-in
import json
import re
import unicodedata
import os
import importlib.util

# Audio
import vosk
import pyaudio
import simpleaudio as sa

# Settings
from settings import TTS_OPEN_REC, TTS_CLOSE_REC, TTS_UNDO_REC


def execute_action(action_key, user_input):
    """
    Esegue tutti gli step definiti per una specifica azione.
    """
    action_steps = get_action_registry().get(action_key, {}).get("steps", [])
    context = {"user_input": user_input}

    for step in action_steps:
        function = step["function"]
        input_value = context.get(step["input_key"])
        if input_value is not None:
            output_value = function(input_value)
            context[step["output_key"]] = output_value

    return context.get("final_response", None)


# Funzione per catturare il testo tramite Vosk
def capture_speech():
    model = vosk.Model("models/vosk-model-it")  # Update the path to the model if needed
    recognizer = vosk.KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=4096,
    )
    stream.start_stream()
    print(
        f"""
        Per evocare il tuo assistente vocale, pronuncia '{TTS_OPEN_REC}'.
        Parla e pronuncia chiaramente le tue richieste. Quando hai finito, pronuncia '{TTS_CLOSE_REC}'.
        Per annullare la registrazione, pronuncia '{TTS_UNDO_REC}'.\n
        """
    )

    is_recording = False
    captured_text = []

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result["text"].strip().lower()

            if text == TTS_OPEN_REC.lower():
                print("\n🎤 Registrazione iniziata! Parla...\n")
                is_recording = True
                captured_text = []
            elif text == TTS_CLOSE_REC.lower():
                print("\n🛑 Registrazione terminata!\n")
                break
            elif text == TTS_UNDO_REC.lower():
                print("\n❌ Registrazione annullata!\n")
                captured_text = []
                return None
            elif is_recording and text:
                captured_text.append(text)

    return " ".join(captured_text)


# Funzione per riprodurre l'audio
def play_audio(audio_file):
    print(f"▶️ Riproduzione audio: {audio_file}")
    wave_obj = sa.WaveObject.from_wave_file(audio_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def clean_text_for_tts(text):
    """
    Pulisce il testo prima di convertirlo in audio.
    Rimuove caratteri non supportati, simboli speciali, sostituisce numeri con parole e assicura una lunghezza minima.
    """
    # Normalizza il testo rimuovendo caratteri speciali Unicode
    text = unicodedata.normalize("NFKD", text)

    # Rimuove parentesi graffe e altri caratteri non supportati
    text = re.sub(r"[{}\[\]<>]", "", text)

    # Sostituisce il simbolo % con "percento"
    text = text.replace("%", " percento")

    # Sostituisce simboli comuni con testo leggibile
    replacements = {
        "$": " dollari",
        "€": " euro",
        "&": " e ",
        "@": " chiocciola ",
        "#": " hashtag ",
        "*": "  ",
        "~": " tilde ",
        "^": " elevato alla ",
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    # Rimuove caratteri non alfabetici isolati (ad esempio, caratteri di controllo o simboli strani)
    text = re.sub(r"[^a-zA-Z0-9À-ÿ.,!?()'\"\s]", "", text)

    # Rimuove spazi extra
    text = re.sub(r"\s+", " ", text).strip()

    # Assicura una lunghezza minima per evitare errori di sintesi vocale
    if len(text) < 50:
        text += " Questo è un messaggio di riempimento per garantire una lunghezza sufficiente."

    return text


def get_action_registry():
    """
    Scansiona la cartella delle actions e restituisce il dizionario ACTIONS.
    """
    actions_dir = os.path.join(os.path.dirname(__file__), "actions")
    actions_registry = {}

    for filename in os.listdir(actions_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"actions.{filename[:-3]}"
            module_path = os.path.join(actions_dir, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Controlla se il modulo ha ACTION_CHAIN
            if hasattr(module, "ACTION_CHAIN"):
                action_chain = getattr(module, "ACTION_CHAIN")
                if "metadata" in action_chain and "name" in action_chain["metadata"]:
                    action_name = action_chain["metadata"]["name"]
                    actions_registry[action_name] = action_chain

    return actions_registry
