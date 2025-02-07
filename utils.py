# Built-in
import json
import re
import unicodedata

# Audio
import vosk
import pyaudio
import simpleaudio as sa


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

            if text == "computer attivati":
                print("\n🎤 Registrazione iniziata! Parla...\n")
                is_recording = True
                captured_text = []
            elif text == "computer elabora":
                print("\n🛑 Registrazione terminata!\n")
                break
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
        "*": " asterisco ",
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
