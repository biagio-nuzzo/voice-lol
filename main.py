# Built-in
import json
import re

# Api
import requests

# Audio
import vosk
import pyaudio
import simpleaudio as sa

# TTS Modules
from tts_modules.tts_tts import generate_audio_tts
from tts_modules.bark_tts import generate_audio_bark

# Constants
from data.constants.items import LOL_ITEMS

# Settings
from settings import API_URL, TTS_MODEL


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
        """
        Per evocare il tuo assistente vocale, pronuncia 'Ombra attivati'. 
        Parla e pronuncia chiaramente le tue richieste. Quando hai finito, pronuncia 'Ombra agisci'.
        """
    )

    is_recording = False
    captured_text = []

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result["text"].strip().lower()

            if text == "ombra attivati":
                print("\n🎤 Registrazione iniziata! Parla...\n")
                is_recording = True
                captured_text = []
            elif text == "ombra agisci":
                print("\n🛑 Registrazione terminata!\n")
                break
            elif is_recording and text:
                captured_text.append(text)

    return " ".join(captured_text)


# Funzione per interrogare l'LLM
def llm_get_item(user_input):
    pre_prompt = f"""
Sei un sistema di identificazione per oggetti di League of Legends. Il tuo compito è **solo** restituire un JSON nel seguente formato:

{{
    "item": "NOME_OGGETTO"
}}

Dove **NOME_OGGETTO** è uno dei seguenti valori esatti:
- "LAMA_DI_DORAN"
- "SIGILLO_OSCURO"
- "CORAZZA_UOMO_MORTO"
- "ARCO_SCUDO_IMMORTALE"
- "MASCHERA_ABISSO"

Se la richiesta dell'utente riguarda uno di questi oggetti, restituisci **solo il JSON corretto**. Se la richiesta non riguarda uno di questi oggetti, restituisci:

{{
    "item": null
}}

⚠️ **Regole importanti:**  
1. **Non fornire spiegazioni.**  
2. **Non generare più di un JSON.**  
3. **Non aggiungere testo prima o dopo il JSON.**  

**Input:** "{user_input}"
    """

    payload = {
        "model": "gemma-2-2b-instruct",
        "prompt": pre_prompt,
        "max_tokens": 200,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()["choices"][0]["text"]
        match = re.search(r'\{\s*"item"\s*:\s*"(.*?)"\s*\}', data)
        if match:
            return {"item": match.group(1)}

    print(f"Errore nella richiesta: {response.status_code}")
    return {"item": None}


# Funzione per generare una descrizione dettagliata
def generate_description(item_key):
    item_info = LOL_ITEMS[item_key]
    description_prompt = f"""
Genera una descrizione tra i 180 - 280 caratteri per il seguente oggetto di League of Legends:

Nome: {item_key.replace('_', ' ')}
Descrizione: {item_info['description']}
Statistiche: {json.dumps(item_info['statistics'], indent=4)}
Effetti: {item_info['effects']}

Restituisci solo la descrizione testuale.
    """

    payload = {
        "model": "gemma-2-2b-instruct",
        "prompt": description_prompt,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()

    return "Errore nella generazione della descrizione."


# Funzione per riprodurre l'audio
def play_audio(audio_file):
    print(f"▶️ Riproduzione audio: {audio_file}")
    wave_obj = sa.WaveObject.from_wave_file(audio_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


# Funzione principale
def main():
    while True:
        text = capture_speech()
        if text:
            print(f"📜 Testo registrato: {text}")
            item_data = llm_get_item(text)
            item_key = item_data.get("item")

            if item_key:
                print(f"🔹 Item identificato: {item_key}")
                if item_key in LOL_ITEMS:
                    description = generate_description(item_key)
                    print("📢 Descrizione generata:")
                    print(description)

                    # Generazione audio
                    print("🔊 Generazione audio in corso...")

                    if TTS_MODEL == "TTS":
                        audio_file = generate_audio_tts(description, item_key)
                    else:
                        audio_file = generate_audio_bark(description, item_key)

                    print(f"🔊 Audio generato: {audio_file}")

                    # Riproduzione audio
                    play_audio(audio_file)
                else:
                    print("⚠️ Oggetto non riconosciuto.")


if __name__ == "__main__":
    main()
