# Built-in
import json
import os

# Vosk
import vosk
import pyaudio

# PyQt5
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal

# Fastchain
from fastchain.core import Action

# Ottieni il percorso corretto del modello
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-it")


class SpeechInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrazione Vocale")
        self.setFixedSize(400, 250)

        self.layout = QVBoxLayout()

        # Riquadro per mostrare il testo acquisito
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.layout.addWidget(self.text_display)

        # Pulsante per interrompere la registrazione
        self.stop_button = QPushButton("Stop Registrazione", self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

        self.recording_thread = SpeechRecorderThread()
        self.recording_thread.partial_result.connect(self.update_text_display)
        self.recording_thread.finished.connect(self.on_recording_finished)
        self.result_text = ""

    def start_recording(self):
        self.recording_thread.start()
        self.exec_()
        return self.result_text  # Restituisce il testo catturato

    def update_text_display(self, text):
        """Aggiorna il testo visualizzato nel dialogo"""
        self.text_display.append(text.strip())

    def stop_recording(self):
        """Ferma la registrazione e chiude il dialogo"""
        self.recording_thread.stop()
        self.recording_thread.wait()
        self.accept()

    def on_recording_finished(self, text):
        """Gestisce la fine della registrazione"""
        self.result_text = text.strip()
        self.text_display.append(self.result_text)
        self.accept()


class SpeechRecorderThread(QThread):
    partial_result = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.speech_action = CaptureSpeechAction()
        self.result_text = ""

    def run(self):
        for text in self.speech_action.execute():
            self.partial_result.emit(text)
            self.result_text += text + " "
        self.finished.emit(self.result_text.strip())

    def stop(self):
        self.speech_action.stop()
        self.wait()


class CaptureSpeechAction:
    """Classe per avviare il riconoscimento vocale"""

    model = None  # Modello caricato solo una volta

    def __init__(self):
        if CaptureSpeechAction.model is None:
            print("[INFO] Caricamento modello Vosk...")
            CaptureSpeechAction.model = vosk.Model(MODEL_PATH)
        self.recognizer = vosk.KaldiRecognizer(CaptureSpeechAction.model, 44100)
        self.mic = pyaudio.PyAudio()
        self.should_stop = False

    def execute(self):
        """Avvia il riconoscimento vocale e restituisce il testo progressivamente."""
        input_device_index = None
        for i in range(self.mic.get_device_count()):
            device_info = self.mic.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                input_device_index = i
                break

        if input_device_index is None:
            print("[ERROR] Nessun microfono disponibile.")
            return "Nessun microfono disponibile."

        stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=2048,
            input_device_index=input_device_index,
        )
        stream.start_stream()

        full_text = ""
        try:
            print("[EXEC] Inizio registrazione. Parla ora...")
            while not self.should_stop:
                data = stream.read(2048, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result["text"].strip()
                    if text:
                        full_text += " " + text
                        yield text
                else:
                    partial_result = json.loads(self.recognizer.PartialResult())
                    partial_text = partial_result.get("partial", "").strip()
                    if partial_text:
                        print("[STEP] Parziale:", partial_text)
                        yield partial_text
        except KeyboardInterrupt:
            print("[ERROR] Interruzione del riconoscimento.")
        finally:
            stream.stop_stream()
            stream.close()
            self.mic.terminate()
            print("[EXEC] Fine registrazione:", full_text.strip())
            yield full_text.strip()

    def stop(self):
        """Ferma la registrazione"""
        self.should_stop = True


def test(input):
    print("INPUTOOO", input)


CAPTURE_SPEECH_ACTION = Action(
    name="CAPTURE_SPEECH",
    description="Registra l'audio dell'utente e lo converte in testo, restituendo l'output come input per altre azioni.",
    verbose_name="Registrazione Vocale",
    steps=[
        {
            "function": lambda: SpeechInputDialog().start_recording(),
            "input_type": None,
            "output_type": str,
        },
        {
            "function": test,
            "input_type": str,
            "output_type": None,
        },
    ],
    input_action=True,
)
