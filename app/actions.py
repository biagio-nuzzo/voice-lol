from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QPushButton
from app.dialogs import SpeechRecognitionDialog
from app.recognition import SpeechRecognitionManager


class ActionsPanel(QWidget):
    """Sezione della UI che contiene tutti i pulsanti delle action"""

    def __init__(self):
        super().__init__()

        self.recognition_manager = SpeechRecognitionManager()

        layout = QVBoxLayout()

        # Sezione scrollabile per i pulsanti delle action
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.action_frame = QWidget()
        self.action_layout = QVBoxLayout(self.action_frame)

        # Aggiunta del pulsante per il riconoscimento vocale
        self.start_voice_button = QPushButton("Avvia Riconoscimento Vocale")
        self.start_voice_button.clicked.connect(self.start_voice_recognition)
        self.action_layout.addWidget(self.start_voice_button)

        self.scroll_area.setWidget(self.action_frame)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def start_voice_recognition(self):
        """Avvia la finestra di riconoscimento vocale"""
        dialog = SpeechRecognitionDialog(self.recognition_manager)
        dialog.exec_()
