# PyQt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from PyQt5.QtCore import Qt

# Audio recognition
from app.actions.core.capture_speech.recognition import SpeechRecognitionThread


class SpeechRecognitionWorker(QObject):
    """Worker per il riconoscimento vocale senza bloccare la UI"""

    result_signal = pyqtSignal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.running = True
        self.thread = None  # Thread Python

    def run(self):
        """Esegue il riconoscimento vocale in un thread Python"""
        self.thread = threading.Thread(target=self._recognize)
        self.thread.start()

    def _recognize(self):
        """Esegue la logica di riconoscimento vocale"""
        recognition_thread = SpeechRecognitionThread(self.model)
        recognition_thread.result_signal.connect(self.result_signal.emit)
        recognition_thread.run()  # Eseguiamo direttamente senza PyQt QThread

    def stop(self):
        """Ferma il riconoscimento vocale"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()


class SpeechRecognitionDialog(QDialog):
    """Finestra di dialogo per il riconoscimento vocale"""

    def __init__(self, recognition_manager):
        super().__init__()
        self.setWindowTitle("Riconoscimento Vocale")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(400, 300)

        self.recognition_manager = recognition_manager

        # Layout
        self.layout = QVBoxLayout()

        # Area di testo scrollabile
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFixedHeight(150)
        self.layout.addWidget(self.text_area)

        # Pulsante per stoppare la registrazione
        self.stop_button = QPushButton("Stop Registrazione")
        self.stop_button.clicked.connect(self.stop_and_notify_main_ui)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)
        self.full_text = ""

        # Creiamo il worker come un oggetto normale (senza QThread)
        self.worker_thread = SpeechRecognitionWorker(self.recognition_manager.model)

        # Creiamo un vero thread Python per avviare il worker
        self.worker_process = threading.Thread(target=self.worker_thread.run)

        # Connettiamo il segnale del worker al metodo `update_text`
        self.worker_thread.result_signal.connect(self.update_text)

        # Avviamo il thread
        self.worker_process.start()

    def update_text(self, text):
        """Aggiorna il testo nella text area nel main thread"""
        self.full_text += text + "\n"
        self.text_area.setText(self.full_text)
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        """Intercetta la chiusura del dialogo per evitare che chiuda l'intera app"""
        self.hide()  # Nasconde la finestra invece di chiuderla
        event.ignore()  # Evita la chiusura completa dell'applicazione

    def stop_and_notify_main_ui(self):
        """Ferma il riconoscimento vocale e informa la UI principale"""
        self.stop_recording()
        if hasattr(self.recognition_manager, "main_ui"):
            self.recognition_manager.main_ui.stop_capture_speech()  # Chiama il metodo in MainUI

    def stop_recording(self):
        """Ferma il riconoscimento vocale in modo sicuro senza chiudere l'app"""
        if self.worker_process and self.worker_process.is_alive():
            self.worker_thread.running = False  # Ferma il worker
            self.worker_process.join()  # Aspetta che il thread finisca

        # Nascondi il dialogo invece di chiuderlo
        self.hide()
        print("Registrazione fermata, dialogo nascosto.")  # Debug
