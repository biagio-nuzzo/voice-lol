# PyQt
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

# Global States
from app.ui.global_states import state

# Capture Speech Thread
from app.actions.core.capture_speech.capture_speech_thread import SpeechRecorderThread


class SpeechRecorderController(QObject):
    recording_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.recorder_thread = None
        # Timer per verificare lo stato globale e forzare lo stop se necessario
        self.state_timer = QTimer(self)
        self.state_timer.setInterval(500)
        self.state_timer.timeout.connect(self.poll_recording_state)
        self.state_timer.start()

    def poll_recording_state(self):
        if not state["recording"] and self.is_recording:
            print(
                "[Controller] QTimer: stato globale 'recording' False, forzo stop del thread."
            )
            if self.recorder_thread:
                self.recorder_thread.stop()
                if self.recorder_thread.isRunning():
                    self.recorder_thread.terminate()
                    print("[Controller] QTimer: thread terminato forzatamente.")
            self.is_recording = False
            self.recording_state_changed.emit(self.is_recording)

    def start_capture(self, next_action):
        if next_action is None:
            raise ValueError("La next_action deve essere passata a start_capture.")
        state["next_action"] = next_action

        if self.is_recording:
            print("[Controller] Tentativo di avviare una registrazione già in corso.")
            return

        print("[Controller] Avviando la registrazione...")
        self.recorder_thread = SpeechRecorderThread()
        self.recorder_thread.finished.connect(self.on_recording_finished)
        self.recorder_thread.start()

        self.is_recording = True
        state["recording"] = True
        self.recording_state_changed.emit(self.is_recording)

    def stop_capture(self):
        print("[Controller] Fermando la registrazione...")
        if self.recorder_thread:
            self.recorder_thread.stop()
            if self.recorder_thread.stream:
                try:
                    self.recorder_thread.stream.stop_stream()
                except Exception as e:
                    print("[Controller] Errore nello stop dello stream:", e)
        self.is_recording = False
        state["recording"] = False
        self.recording_state_changed.emit(self.is_recording)
        if not state.get("next_action"):
            raise ValueError("La next_action non è stata impostata.")
        from fastchain.manager import FastChainManager

        FastChainManager.run_action(state["next_action"], state["speech_text"])
        state["next_action"] = None

    def on_recording_finished(self, text):
        state["speech_text"] = text
        print(f"[DEBUG] Testo acquisito: {text}")
        self.is_recording = False
        state["recording"] = False
        self.recording_state_changed.emit(self.is_recording)


class CaptureSpeechSingleton:
    _controller_instance = None

    @staticmethod
    def get_controller():
        if CaptureSpeechSingleton._controller_instance is None:
            print("[Singleton] Creazione di una nuova istanza del controller.")
            CaptureSpeechSingleton._controller_instance = SpeechRecorderController()
        return CaptureSpeechSingleton._controller_instance
