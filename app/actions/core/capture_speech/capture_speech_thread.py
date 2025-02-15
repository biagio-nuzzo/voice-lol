# Built-in
import json
import os

# PyQt
from PyQt5.QtCore import QThread, pyqtSignal

# Vosk
import vosk
import pyaudio

# Global States
from app.ui.global_states import (
    state,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-it")


class SpeechRecorderThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.should_stop = False
        self.stream = None  # Riferimento allo stream aperto
        if not hasattr(SpeechRecorderThread, "model"):
            print("[INFO] Caricamento modello Vosk...")
            SpeechRecorderThread.model = vosk.Model(MODEL_PATH)
        self.recognizer = vosk.KaldiRecognizer(SpeechRecorderThread.model, 44100)
        self.mic = pyaudio.PyAudio()

    def run(self):
        # Inizializza il testo registrato nello state globale
        state["speech_text"] = ""
        input_device_index = None
        for i in range(self.mic.get_device_count()):
            device_info = self.mic.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                input_device_index = i
                break

        if input_device_index is None:
            print("[ERROR] Nessun microfono disponibile.")
            self.finished.emit("Nessun microfono disponibile.")
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
        self.stream = stream  # Salva il riferimento allo stream

        full_text = ""
        print("[EXEC] Inizio registrazione. Parla ora...")
        try:
            while not self.should_stop:
                try:
                    data = stream.read(2048, exception_on_overflow=False)
                except Exception as e:
                    print("[ERROR] Errore nella lettura del flusso:", e)
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        full_text += " " + text
                        print(f"[STEP] Testo acquisito: {text}")
                        # Aggiorna lo state globale ad ogni acquisizione
                        state["speech_text"] = full_text.strip()
                    self.recognizer.Reset()
        finally:
            try:
                stream.stop_stream()
            except Exception as e:
                print("[Thread] Errore nello stop dello stream:", e)
            stream.close()
            self.mic.terminate()

            state["speech_text"] = full_text.strip()
            print("[EXEC] Fine registrazione:", state["speech_text"])
            self.finished.emit(state["speech_text"])

    def stop(self):
        self.should_stop = True
