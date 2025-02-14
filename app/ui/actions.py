from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QPushButton, QTextEdit
from PyQt5.QtGui import QFont

# UI Components
from app.actions.core.get_keyboard_input import GetKeyboardInputAction


class ActionsPanel(QWidget):
    """Sezione della UI che contiene tutti i pulsanti delle action"""

    def __init__(self, main_ui):
        super().__init__()

        self.main_ui = main_ui  # Riferimento a MainUI

        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)

        # Terminale live
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet(
            "background-color: black; color: white; font-family: monospace;"
        )
        layout.addWidget(self.terminal_output, 70)

        # Sezione scrollabile per i pulsanti delle action
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.action_frame = QWidget()
        self.action_layout = QVBoxLayout(self.action_frame)
        self.action_layout.setSpacing(2)

        # Stile pulsanti
        button_style = (
            "background-color: #4CAF50;"
            "color: white;"
            "border-radius: 8px;"
            "padding: 10px;"
            "font-size: 16px;"
        )

        # Pulsante per attivare Capture Speech
        self.capture_speech_button = QPushButton("Attivare Capture Speech")
        self.capture_speech_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.capture_speech_button.setStyleSheet(button_style)
        self.capture_speech_button.clicked.connect(self.main_ui.start_capture_speech)
        self.action_layout.addWidget(self.capture_speech_button)

        # Pulsante per ottenere input da tastiera
        self.keyboard_input_button = QPushButton("Get Keyboard Input")
        self.keyboard_input_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.keyboard_input_button.setStyleSheet(button_style)
        self.keyboard_input_button.clicked.connect(
            lambda: self.log_output(GetKeyboardInputAction().execute())
        )
        self.action_layout.addWidget(self.keyboard_input_button)

        self.scroll_area.setWidget(self.action_frame)
        layout.addWidget(self.scroll_area, 40)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #2C3E50; color: white; padding: 10px;")

    def log_output(self, output):
        """Stampa il testo nel terminale live"""
        self.terminal_output.append(output)
