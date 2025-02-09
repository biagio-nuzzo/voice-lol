import vosk
import pyaudio
import json
import sys
import select


def capture_speech_action():
    """
    Avvia la registrazione audio e la converte in testo.
    L'utente può parlare e premere INVIO per terminare la registrazione.
    """
    model = vosk.Model("models/vosk-model-it")
    recognizer = vosk.KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()

    # Apertura dello stream audio
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=2048,  # 🔹 Buffer ridotto per una migliore acquisizione
    )
    stream.start_stream()

    print("\n🎤 Registrazione avviata! Parla... (Premi INVIO per terminare)\n")

    captured_text = []
    stop_capture = False

    # Loop di registrazione
    while not stop_capture:
        try:
            data = stream.read(2048, exception_on_overflow=False)

            if len(data) == 0:
                print("⚠️ Nessun audio ricevuto. Assicurati che il microfono funzioni.")
                break

            # 🔹 Controlliamo il riconoscimento parziale per un feedback in tempo reale
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result["text"].strip().lower()

                if text:
                    print(f"📝 Riconosciuto: {text}")
                    captured_text.append(text)
            else:
                partial_result = json.loads(recognizer.PartialResult())
                sys.stdout.write(f"\r🕵️ Parziale: {partial_result.get('partial', '')}")
                sys.stdout.flush()

            # Controlliamo se l'utente ha premuto INVIO per fermare la registrazione
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input("\nPremi INVIO per terminare la registrazione...")
                stop_capture = True

        except Exception as e:
            print(f"⚠️ Errore durante la registrazione: {e}")
            break

    print("\n🛑 Registrazione terminata!\n")

    # Stop del microfono
    stream.stop_stream()
    stream.close()
    mic.terminate()

    # 🔹 Se nessun testo è stato riconosciuto, restituire un messaggio di errore
    final_text = (
        " ".join(captured_text)
        if captured_text
        else "Impossibile riconoscere l'audio. Riprova."
    )

    print("\n🔊 Trascrizione audio completata!\n")
    print("Testo riconosciuto:")
    print(final_text)

    return final_text


# Definizione dell'Action
ACTION_CHAIN = {
    "metadata": {
        "name": "CAPTURE_SPEECH",
        "description": "Registra l'audio dell'utente e lo converte in testo quando preme INVIO.",
    },
    "steps": [
        {
            "function": "capture_speech_action",
            "input_key": None,
            "output_key": "speech_text",
        }
    ],
}
