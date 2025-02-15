# Built-in
import json
import os

# PyQt
from PyQt5.QtCore import QThread, pyqtSignal

# Vosk
import vosk
import pyaudio

# FastChain
from fastchain.core import Action

# Percorso del modello Vosk
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-it")

# Variabile globale per salvare il testo acquisito
global_speech_text = ""


class SpeechRecorderThread(QThread):
    """Thread per il riconoscimento vocale con Vosk"""

    finished = pyqtSignal(str)  # Segnale per il testo finale

    def __init__(self):
        super().__init__()
        self.should_stop = False  # Variabile per fermare la registrazione

        # Carichiamo il modello solo una volta
        if not hasattr(SpeechRecorderThread, "model"):
            print("[INFO] Caricamento modello Vosk...")
            SpeechRecorderThread.model = vosk.Model(MODEL_PATH)

        self.recognizer = vosk.KaldiRecognizer(SpeechRecorderThread.model, 44100)
        self.mic = pyaudio.PyAudio()

    def run(self):
        """Avvia la registrazione vocale"""
        global global_speech_text
        global_speech_text = (
            ""  # Puliamo il valore ogni volta che iniziamo una registrazione
        )

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
        try:
            print("[EXEC] Inizio registrazione. Parla ora...")
            while not self.should_stop:
                data = stream.read(2048, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result["text"].strip()
                    if text:
                        full_text += " " + text
                        print(f"[STEP] Testo acquisito: {text}")
        finally:
            stream.stop_stream()
            stream.close()
            self.mic.terminate()

            # Salviamo il valore acquisito nella variabile globale
            global_speech_text = full_text.strip()
            print("[EXEC] Fine registrazione:", global_speech_text)
            self.finished.emit(global_speech_text)  # Segnale con il risultato finale

    def stop(self):
        """Ferma la registrazione"""
        self.should_stop = True


# Manteniamo il riferimento al thread di registrazione
recorder_thread = None


def start_recording():
    """Avvia la registrazione dell'audio in un thread separato"""
    global recorder_thread
    if recorder_thread and recorder_thread.isRunning():
        print("[ERROR] Registrazione già in corso.")
        return

    print("[ACTION] Avvio registrazione...")
    recorder_thread = SpeechRecorderThread()
    recorder_thread.start()


def stop_recording():
    """Ferma la registrazione dell'audio"""
    global recorder_thread
    if not recorder_thread or not recorder_thread.isRunning():
        print("[ERROR] Nessuna registrazione in corso.")
        return

    print("[ACTION] Fermando la registrazione...")
    recorder_thread.stop()
    recorder_thread.wait()  # Aspettiamo la terminazione del thread


def get_recorded_text():
    """Ritorna il valore della registrazione"""
    print(f"[ACTION] Testo acquisito: {global_speech_text}")
    return global_speech_text


START_CAPTURE_SPEECH_ACTION = Action(
    name="START_CAPTURE_SPEECH",
    description="Avvia la registrazione vocale.",
    verbose_name="Avvia Registrazione",
    steps=[
        {
            "function": lambda: start_recording(),
            "input_type": None,
            "output_type": None,
        },
    ],
    input_action=True,
)

STOP_CAPTURE_SPEECH_ACTION = Action(
    name="STOP_CAPTURE_SPEECH",
    description="Ferma la registrazione vocale e restituisce il testo acquisito.",
    verbose_name="Ferma Registrazione",
    steps=[
        {
            "function": lambda: stop_recording(),
            "input_type": None,
            "output_type": None,
        },
        {
            "function": lambda: get_recorded_text(),
            "input_type": None,
            "output_type": str,
        },
    ],
    input_action=True,
)
