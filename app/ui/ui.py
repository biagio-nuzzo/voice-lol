# PyQt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QTimer

# Global States
from app.ui.global_states import state  # Importa il dizionario globale

# Actions
from app.actions.core.capture_speech.capture_speech_controller import (
    CaptureSpeechSingleton,
)


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")
        self.controller = CaptureSpeechSingleton.get_controller()

        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.toggle_recording)

        # Aggiungo una label per mostrare il valore di speech_text
        self.label_speech_text = QLabel("Speech text: ", self)

        layout = QVBoxLayout()
        layout.addWidget(self.button_record)
        layout.addWidget(self.label_speech_text)
        self.setLayout(layout)

        # Timer per aggiornare il pulsante in base a state["recording"]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_button_text)
        self.timer.start(500)

        # Timer per aggiornare e loggare il valore di state["speech_text"]
        self.speech_text_timer = QTimer(self)
        self.speech_text_timer.timeout.connect(self.update_speech_text)
        self.speech_text_timer.start(1000)

    def toggle_recording(self):
        if state["recording"]:
            self.controller.stop_capture()
        else:
            self.controller.start_capture("PRINT_VALUE")

    def update_button_text(self):
        # Aggiorna il testo del pulsante in base al valore globale di state["recording"]
        if state["recording"]:
            self.button_record.setText("Stop Registrazione")
        else:
            self.button_record.setText("Avvia Registrazione")

    def update_speech_text(self):
        # Logga e aggiorna la label con il valore corrente di state["speech_text"]
        current_text = state.get("speech_text", "")
        self.label_speech_text.setText(f"Speech text: {current_text}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())
