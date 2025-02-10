import vosk
import pyaudio
import json
import sys
import select


def capture_speech_action():
    """
    Avvia la registrazione audio e la converte in testo.
    L'utente può parlare e premere INVIO per terminare la registrazione solo se almeno un testo è stato riconosciuto.
    """
    try:
        # 🔹 Carica il modello Vosk
        model = vosk.Model("models/vosk-model-it")
        recognizer = vosk.KaldiRecognizer(model, 16000)

        # 🔹 Inizializza PyAudio
        mic = pyaudio.PyAudio()

        # 🔹 Trova il dispositivo di input corretto
        input_device_index = None
        for i in range(mic.get_device_count()):
            device_info = mic.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                input_device_index = i
                break

        if input_device_index is None:
            print("⚠️ Nessun microfono disponibile! Controlla le impostazioni audio.")
            return None

        print(
            f"🎤 Usando il microfono: {mic.get_device_info_by_index(input_device_index)['name']}"
        )

        # 🔹 Apertura dello stream audio
        stream = mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=input_device_index,
        )
        stream.start_stream()

        print(
            "\n🎤 Registrazione avviata! Parla... (Premi INVIO per terminare, solo dopo il primo riconoscimento!)\n"
        )

        captured_text = []
        recognized_something = (
            False  # 🔹 Indica se almeno un testo è stato riconosciuto
        )

        # 🔹 Svuota il buffer di input per evitare lag
        stream.read(stream.get_read_available(), exception_on_overflow=False)

        # 🔹 Loop di registrazione
        while True:
            try:
                data = stream.read(1024, exception_on_overflow=False)

                if not data or len(data) == 0:
                    print(
                        "⚠️ Nessun audio ricevuto. Assicurati che il microfono funzioni."
                    )
                    continue

                # 🔹 Controlliamo il riconoscimento parziale per feedback in tempo reale
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result["text"].strip().lower()

                    if text:
                        print(f"📝 Riconosciuto: {text}")
                        captured_text.append(text)
                        recognized_something = (
                            True  # 🔹 Ora possiamo permettere l'uscita
                        )
                else:
                    partial_result = json.loads(recognizer.PartialResult())
                    sys.stdout.write(
                        f"\r🕵️ Parziale: {partial_result.get('partial', '')}"
                    )
                    sys.stdout.flush()

                # 🔹 Controlliamo se l'utente ha premuto INVIO per fermare la registrazione
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    input("\nPremi INVIO per terminare la registrazione...")

                    if not recognized_something:
                        print(
                            "⚠️ Devi parlare prima di poter terminare la registrazione! Continua a parlare."
                        )
                        continue  # 🔹 Impedisce la chiusura finché non è stato riconosciuto almeno un testo

                    break  # 🔹 Se c'è testo riconosciuto, usciamo dal loop

            except Exception as e:
                print(f"⚠️ Errore durante la registrazione: {e}")
                break

        print("\n🛑 Registrazione terminata!\n")

        # 🔹 Elaborazione dell'ultimo frammento di audio
        remaining_data = stream.read(1024, exception_on_overflow=False)
        if remaining_data and recognizer.AcceptWaveform(remaining_data):
            final_result = json.loads(recognizer.Result())
            final_text = final_result["text"].strip().lower()
            if final_text:
                print(f"📝 Ultima parte riconosciuta: {final_text}")
                captured_text.append(final_text)

        # 🔹 Stop del microfono
        stream.stop_stream()
        stream.close()
        mic.terminate()

        print("\n🔊 Trascrizione audio completata!\n")
        print("Testo riconosciuto:", " ".join(captured_text))

        # 🔹 Se nessun testo è stato riconosciuto, restituiamo un messaggio di errore
        final_text = (
            " ".join(captured_text)
            if captured_text
            else "Impossibile riconoscere l'audio. Riprova."
        )

        return final_text

    except Exception as e:
        print(f"⚠️ Errore iniziale: {e}")
        return None


# Definizione dell'Action
ACTION_CHAIN = {
    "metadata": {
        "name": "CAPTURE_SPEECH",
        "description": "Registra l'audio dell'utente e lo converte in testo quando preme INVIO.",
        "input_action": True,
    },
    "steps": [
        {
            "function": "capture_speech_action",
            "input_key": None,
            "output_key": "speech_text",
        }
    ],
}
