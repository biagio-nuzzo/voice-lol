import vosk
import pyaudio
import json


# COSTANTI
# Dizionario con le informazioni sugli oggetti di LoL
lol_items = {
    "LAMA_DI_DORAN": {
        "description": "Oggetto iniziale per campioni da attacco fisico",
        "statistics": {"attacco_fisico": 10, "salute": 100, "rubavita": "3%"},
        "effects": "Aumenta la sopravvivenza e il sustain nei primi trade della partita.",
    },
    "SIGILLO_OSCURO": {
        "description": "Oggetto da neveball per maghi",
        "statistics": {"potere_magico": 15, "salute": 40},
        "effects": "Accumula cariche con uccisioni e assist, aumentando il potere magico.",
    },
    "CORAZZA_UOMO_MORTO": {
        "description": "Oggetto difensivo da tank",
        "statistics": {"salute": 300, "armatura": 45, "velocita_movimento": "5%"},
        "effects": "Accumula velocità di movimento e infligge danni bonus con il primo attacco.",
    },
    "ARCO_SCUDO_IMMORTALE": {
        "description": "Oggetto mitico per ADC e combattenti",
        "statistics": {
            "attacco_fisico": 50,
            "velocita_attacco": "20%",
            "rubavita": "12%",
        },
        "effects": "Fornisce uno scudo e aumenta il rubavita quando la salute è bassa.",
    },
    "MASCHERA_ABISSO": {
        "description": "Oggetto difensivo per tank contro i maghi",
        "statistics": {
            "salute": 500,
            "resistenza_magica": 60,
            "mana": 300,
            "rigenerazione_salute": "100%",
        },
        "effects": "Assorbe danni e li converte in guarigione quando si attacca un nemico.",
    },
}


# SPEECH TO TEXT
# Carica il modello Vosk
model = vosk.Model("vosk-model-it")

# Configura il microfono
recognizer = vosk.KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096
)
stream.start_stream()

print("Parla... (pronuncia 'Void ti evoco' per iniziare la registrazione)")

is_recording = False
captured_text = []

while True:
    data = stream.read(4096, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result["text"].strip().lower()

        print(text)

        if text == "void ti evoco":
            print("\n🎤 Registrazione iniziata! Parla...\n")
            is_recording = True
            captured_text = []
        elif text == "void elabora":
            print("\n🛑 Registrazione terminata!\n")
            break
        elif is_recording and text:
            captured_text.append(text)

# Stampa il testo registrato
final_text = " ".join(captured_text)
print("📜 Testo registrato:")
print(final_text)


# LLM
import requests

# Imposta l'URL dell'API di LM Studio
API_URL = "http://localhost:1234/v1/completions"


pre_prompt = """
Sei un sistema di identificazione per oggetti di League of Legends. Il tuo compito è **solo** restituire un JSON nel seguente formato:

{
    "item": "NOME_OGGETTO"
}

Dove **NOME_OGGETTO** è uno dei seguenti valori esatti:
- "LAMA_DI_DORAN"
- "SIGILLO_OSCURO"
- "CORAZZA_DELL_UOMO_MORTO"
- "ARCO_SCUDO_IMMORTALE"
- "MASCHERA_DELL_ABISSO"

Se la richiesta dell'utente riguarda uno di questi oggetti, restituisci **solo il JSON corretto**.
Se la richiesta non riguarda uno di questi oggetti, restituisci quella più simile.

⚠️ **Regole importanti:**  
1. **Non fornire spiegazioni.**  
2. **Non generare più di un JSON.**  
3. **Non aggiungere testo prima o dopo il JSON.**  
4. **Non modificare il formato del JSON.**
5. **FORNISCI SOLO UNA RISPOSTA**
6. **FORNISCI SEMPRE UNA RISPOSTA**

**Input:** "{testo}"
"""


# Corpo della richiesta
payload = {
    "model": "gemma-2-2b-instruct",  # Sostituisci con il nome del tuo modello caricato su LM Studio
    "prompt": pre_prompt,
    "max_tokens": 200,
    "temperature": 0.7,
}

# Invia la richiesta POST
response = requests.post(API_URL, json=payload)

# Controlla la risposta
if response.status_code == 200:
    data = response.json()
    print("Risposta del modello:")
    print(data["choices"][0]["text"])
else:
    print(f"Errore nella richiesta: {response.status_code}")
    print(response.text)
