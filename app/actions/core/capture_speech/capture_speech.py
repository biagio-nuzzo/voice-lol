# Built-in
import json
import os

# Vosk
import vosk
import pyaudio

# PyQt5
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

# Fastchain
from fastchain.core import Action

# Ottieni il percorso corretto del modello
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-it")


class CaptureSpeechAction:
    """Classe per avviare il riconoscimento vocale"""

    def __init__(self):
        self.model = vosk.Model(MODEL_PATH)
        self.recognizer = vosk.KaldiRecognizer(self.model, 44100)
        self.mic = pyaudio.PyAudio()
        self.should_stop = False  # Flag per fermare la registrazione

    def execute(self):
        """Avvia il riconoscimento vocale e restituisce il testo progressivamente"""
        input_device_index = None
        for i in range(self.mic.get_device_count()):
            device_info = self.mic.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                input_device_index = i
                break

        if input_device_index is None:
            yield "Nessun microfono disponibile."
            return

        stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=2048,
            input_device_index=input_device_index,
        )
        stream.start_stream()

        try:
            print("Inizio registrazione. Parla ora...")
            while not self.should_stop:
                data = stream.read(2048, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result["text"].strip()
                    if text:
                        yield text  # Invia il testo parziale
                        print("Riconosciuto:", text)
                else:
                    partial_result = json.loads(self.recognizer.PartialResult())
                    partial_text = partial_result.get("partial", "").strip()
                    if partial_text:
                        yield partial_text  # Invia il testo parziale
                        print("Parziale:", partial_text)
        except KeyboardInterrupt:
            print("Interruzione del riconoscimento.")
        finally:
            stream.stop_stream()
            stream.close()
            self.mic.terminate()
            yield "Registrazione completata."

    def stop(self):
        """Ferma la registrazione"""
        self.should_stop = True


class SpeechRecorderThread(QThread):
    partial_result = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.should_stop = False
        self.mutex = QMutex()

    def run(self):
        speech_action = CaptureSpeechAction()
        self.full_text = ""  # Memorizza tutto il testo progressivamente
        for text in speech_action.execute():
            self.mutex.lock()
            if self.should_stop:
                self.mutex.unlock()
                break

            # Aggiungiamo il testo nuovo se non è già incluso
            if text and text not in self.full_text:
                self.full_text += " " + text if self.full_text else text
                self.partial_result.emit(
                    self.full_text.strip()
                )  # Invia tutto il testo progressivo

            self.mutex.unlock()

        self.finished.emit("Registrazione completata")

    def stop(self):
        self.mutex.lock()
        self.should_stop = True
        self.mutex.unlock()


CAPTURE_SPEECH_ACTION = Action(
    name="CAPTURE_SPEECH",
    description="Registra l'audio dell'utente e lo converte in testo, restituendo l'output come input per altre azioni.",
    verbose_name="Registrazione Vocale",
    steps=[
        {
            "function": SpeechRecorderThread,
            "input_type": None,
            "output_type": str,
        }
    ],
    input_action=True,
)
