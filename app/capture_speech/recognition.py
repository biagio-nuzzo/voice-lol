import json
import vosk
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal

# Percorso del modello Vosk
MODEL_PATH = "actions/core/capture_speech/models/vosk-model-it"


class SpeechRecognitionManager:
    """Gestisce il modello Vosk e la registrazione audio"""

    def __init__(self):
        print("Caricamento del modello Vosk...")
        self.model = vosk.Model(MODEL_PATH)


class SpeechRecognitionThread(QThread):
    """Thread per la registrazione audio e il riconoscimento vocale"""

    result_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.running = True
        self.model = model
        self.stop_signal.connect(self.stop)
        self.final_text = ""
        self.stream = None
        self.mic = None

    def run(self):
        try:
            recognizer = vosk.KaldiRecognizer(self.model, 44100)
            self.mic = pyaudio.PyAudio()

            input_device_index = None
            for i in range(self.mic.get_device_count()):
                device_info = self.mic.get_device_info_by_index(i)
                if device_info["maxInputChannels"] > 0:
                    input_device_index = i
                    break

            if input_device_index is None:
                self.result_signal.emit("Nessun microfono disponibile.")
                return

            self.stream = self.mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=2048,
                input_device_index=input_device_index,
            )
            self.stream.start_stream()

            captured_text = []
            while self.running:
                data = self.stream.read(2048, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result["text"].strip()
                    if text:
                        captured_text.append(text)
                        self.final_text = " ".join(captured_text)
                        self.result_signal.emit(self.final_text)
                else:
                    partial_result = json.loads(recognizer.PartialResult())
                    partial_text = partial_result.get("partial", "").strip()
                    if partial_text:
                        self.result_signal.emit(partial_text)

        except Exception as e:
            self.result_signal.emit(f"Errore nella registrazione: {e}")

        finally:
            self.close_audio_resources()

    def stop(self):
        """Ferma la registrazione e chiude correttamente le risorse."""
        self.running = False
        self.close_audio_resources()
        self.result_signal.emit(self.final_text)

    def close_audio_resources(self):
        """Chiude PyAudio in modo sicuro"""
        if self.stream is not None:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            except OSError as e:
                print(f"Errore nella chiusura dello stream: {e}")
            finally:
                self.stream = None

        if self.mic is not None:
            try:
                self.mic.terminate()
            except OSError as e:
                print(f"Errore nella chiusura di PyAudio: {e}")
            finally:
                self.mic = None
