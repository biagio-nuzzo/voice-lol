# PyQt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit

# Audio recognition
from app.capture_speech.recognition import SpeechRecognitionThread


class SpeechRecognitionDialog(QDialog):
    """Finestra di dialogo per il riconoscimento vocale"""

    def __init__(self, recognition_manager):
        super().__init__()
        self.setWindowTitle("Riconoscimento Vocale")
        self.setModal(True)
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
        self.stop_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)
        self.full_text = ""

        # Avvia la registrazione
        self.thread = SpeechRecognitionThread(self.recognition_manager.model)
        self.thread.result_signal.connect(self.update_text)
        self.thread.start()

    def update_text(self, text):
        """Aggiorna il testo nella text area"""
        self.full_text += text + "\n"
        self.text_area.setText(self.full_text)
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )

    def stop_recording(self):
        """Ferma il riconoscimento vocale"""
        if self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.accept()
