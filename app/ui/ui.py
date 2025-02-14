# PyQt5
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTextEdit

# Actions
from actions.core.capture_speech.capture_speech import CAPTURE_SPEECH_ACTION


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.recording_thread = None

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")

        self.button = QPushButton("Avvia Registrazione", self)
        self.button.clicked.connect(self.toggle_recording)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text_display)
        self.setLayout(layout)

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.button.setText("Avvia Registrazione")
            self.recording_thread.stop()  # Ferma il thread di registrazione
        else:
            self.is_recording = True
            self.button.setText("Interrompi Registrazione")
            self.text_display.clear()  # Pulisce il testo precedente
            self.start_recording()

    def start_recording(self):
        self.recording_thread = CAPTURE_SPEECH_ACTION.execute()
        self.recording_thread.partial_result.connect(self.update_text_display)
        self.recording_thread.finished.connect(self.on_recording_finished)
        self.recording_thread.start()

    def update_text_display(self, text):
        self.text_display.setPlainText(
            text
        )  # Aggiorna il testo mantenendo il contenuto completo

    def on_recording_finished(self, text):
        self.text_display.append(text)
        self.is_recording = False
        self.button.setText("Avvia Registrazione")
