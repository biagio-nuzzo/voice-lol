# PyQt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject
import threading

# UI Components
from app.ui.actions import ActionsPanel
from app.actions.core.capture_speech.recognition import SpeechRecognitionManager
from app.ui.dialogs import SpeechRecognitionDialog


class CaptureSpeechWorker(QObject):
    """Worker che avvia il riconoscimento vocale senza bloccare la UI"""

    open_dialog = pyqtSignal()

    def __init__(self, recognition_manager):
        super().__init__()
        self.recognition_manager = recognition_manager
        self.thread = None  # Nuovo thread Python

    def run(self):
        """Avvia il riconoscimento vocale in un thread Python"""
        self.thread = threading.Thread(target=self._run_dialog)
        self.thread.start()

    def _run_dialog(self):
        """Esegue il dialogo di riconoscimento vocale nel main thread"""
        self.open_dialog.emit()

    def stop(self):
        """Ferma il worker in modo sicuro"""
        if self.thread and self.thread.is_alive():
            self.thread.join()


class MainUI(QWidget):
    """Interfaccia principale con pulsanti per tutte le action"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastChain - Voice Agent")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Creazione dei worker all'avvio
        self.recognition_manager = SpeechRecognitionManager()
        self.recognition_manager.main_ui = (
            self  # Passa MainUI alla gestione del riconoscimento vocale
        )

        self.capture_speech_worker = CaptureSpeechWorker(self.recognition_manager)
        self.capture_speech_worker.open_dialog.connect(self.open_speech_dialog)

        # Creazione del pannello azioni
        self.actions_panel = ActionsPanel(self)
        layout.addWidget(self.actions_panel)

        self.setLayout(layout)

    def start_capture_speech(self):
        """Avvia il riconoscimento vocale usando il worker esistente"""
        if (
            not self.capture_speech_worker.thread
            or not self.capture_speech_worker.thread.is_alive()
        ):
            self.capture_speech_worker.run()

    def stop_capture_speech(self):
        """Ferma il riconoscimento vocale senza chiudere l'app"""
        if self.capture_speech_worker and self.capture_speech_worker.thread.is_alive():
            self.capture_speech_worker.stop()

        print("Riconoscimento vocale fermato.")  # Debug

        # IMPORTANTE: Se la finestra si chiude per errore, riaprila
        if not self.isVisible():
            self.show()

    def open_speech_dialog(self):
        """Apre il dialogo dal main thread"""
        dialog = SpeechRecognitionDialog(self.recognition_manager)
        dialog.exec_()
