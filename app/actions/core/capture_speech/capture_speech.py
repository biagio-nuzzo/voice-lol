# capture_speech.py
import json
import os
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import vosk
import pyaudio
from fastchain.core import Action

from app.ui.global_states import state  # Importa il dizionario globale

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-it")

global_speech_text = ""


class SpeechRecorderThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.should_stop = False
        if not hasattr(SpeechRecorderThread, "model"):
            print("[INFO] Caricamento modello Vosk...")
            SpeechRecorderThread.model = vosk.Model(MODEL_PATH)
        self.recognizer = vosk.KaldiRecognizer(SpeechRecorderThread.model, 44100)
        self.mic = pyaudio.PyAudio()

    def run(self):
        global global_speech_text
        global_speech_text = ""
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
                    self.recognizer.Reset()
        finally:
            stream.stop_stream()
            stream.close()
            self.mic.terminate()

            global_speech_text = full_text.strip()
            print("[EXEC] Fine registrazione:", global_speech_text)
            self.finished.emit(global_speech_text)

    def stop(self):
        self.should_stop = True


class SpeechRecorderController(QObject):
    recording_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.recorder_thread = None

    def start_capture(self, next_action_name=None):
        if self.is_recording:
            print("[Controller] Tentativo di avviare una registrazione già in corso.")
            return

        print("[Controller] Avviando la registrazione...")
        self.recorder_thread = SpeechRecorderThread()
        self.recorder_thread.next_action_name = next_action_name
        self.recorder_thread.finished.connect(self.on_recording_finished)
        self.recorder_thread.start()

        self.is_recording = True
        state["recording"] = True  # Aggiorna lo stato globale
        self.recording_state_changed.emit(self.is_recording)

    def stop_capture(self):
        if not self.is_recording:
            print("[Controller] Nessuna registrazione in corso.")
            return

        print("[Controller] Fermando la registrazione...")
        if self.recorder_thread:
            self.recorder_thread.stop()
        self.is_recording = False
        state["recording"] = False  # Aggiorna lo stato globale
        self.recording_state_changed.emit(self.is_recording)

    def on_recording_finished(self, text):
        global global_speech_text
        global_speech_text = text
        print(f"[DEBUG] Testo acquisito: {text}")
        self.is_recording = False
        state["recording"] = False  # Aggiorna lo stato globale
        self.recording_state_changed.emit(self.is_recording)


class CaptureSpeechSingleton:
    _controller_instance = None

    @staticmethod
    def get_controller():
        if CaptureSpeechSingleton._controller_instance is None:
            print("[Singleton] Creazione di una nuova istanza del controller.")
            CaptureSpeechSingleton._controller_instance = SpeechRecorderController()
        return CaptureSpeechSingleton._controller_instance


def trigger_next_action(speech_text, next_action_name):
    from fastchain.manager import FastChainManager

    next_action = FastChainManager.run_action(next_action_name, speech_text)
    if next_action:
        print(f"[MANAGER] Esecuzione azione successiva: {next_action_name}")
    else:
        print("[MANAGER] Nessuna azione successiva, ciclo terminato.")


# --- Funzioni per le action distinte ---


def create_toggle_button():
    from PyQt5.QtWidgets import QPushButton

    controller = CaptureSpeechSingleton.get_controller()
    button = QPushButton("Avvia Registrazione")

    def on_click():
        from global_state import state  # Importa lo stato globale

        if state["recording"]:
            controller.stop_capture()
            button.setText("Avvia Registrazione")
            print("[UI] Registrazione fermata tramite bottone toggle.")
        else:
            controller.start_capture()
            button.setText("Stop Registrazione")
            print("[UI] Registrazione avviata tramite bottone toggle.")

    button.clicked.connect(on_click)
    return button


def start_capture_action(next_action_name=None):
    CaptureSpeechSingleton.get_controller().start_capture(next_action_name)
    print("[ACTION] start_capture_action eseguita.")


def stop_capture_action():
    CaptureSpeechSingleton.get_controller().stop_capture()
    print("[ACTION] stop_capture_action eseguita.")


WIDGET_TOGGLE_CAPTURE = Action(
    name="WIDGET_TOGGLE_CAPTURE",
    description="Restituisce un widget (pulsante) che permette di attivare/disattivare la registrazione.",
    verbose_name="Pulsante Toggle Registrazione",
    steps=[
        {
            "function": create_toggle_button,
            "input_type": None,
            "output_type": "QWidget",
        }
    ],
    input_action=False,
)

START_CAPTURE = Action(
    name="START_CAPTURE",
    description="Avvia la registrazione vocale.",
    verbose_name="Avvia Registrazione",
    steps=[
        {
            "function": start_capture_action,
            "input_type": str,
            "output_type": None,
        }
    ],
    input_action=True,
)

STOP_CAPTURE = Action(
    name="STOP_CAPTURE",
    description="Ferma la registrazione vocale.",
    verbose_name="Ferma Registrazione",
    steps=[
        {
            "function": stop_capture_action,
            "input_type": None,
            "output_type": None,
        }
    ],
    input_action=False,
)
