from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTextEdit, QApplication
from app.actions.core.capture_speech.capture_speech import (
    SpeechInputDialog,
)  # Importiamo il dialogo per la registrazione vocale
from fastchain.manager import FastChainManager


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")

        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.start_recording_dialog)

        self.button_input = QPushButton("Inserisci Testo", self)
        self.button_input.clicked.connect(self.get_user_input)

        layout = QVBoxLayout()
        layout.addWidget(self.button_record)
        layout.addWidget(self.button_input)
        self.setLayout(layout)

    def start_recording_dialog(self):
        """Apre il dialog di registrazione vocale."""
        dialog = SpeechInputDialog(self)
        dialog.exec_()  # Esegue il dialogo in modalità bloccante

    def get_user_input(self):
        """Apre la finestra per l'input testuale."""
        FastChainManager.run_action("GET_KEYBOARD_INPUT")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())
