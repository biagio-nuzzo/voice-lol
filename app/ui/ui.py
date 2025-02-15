# PyQt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QApplication

# FastChain
from fastchain.manager import FastChainManager


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False  # Stato della registrazione

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")

        # Bottone per gestire la registrazione vocale
        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.toggle_recording)

        # Bottone per input da tastiera
        self.button_input = QPushButton("Inserisci Testo", self)
        self.button_input.clicked.connect(self.get_user_input)

        layout = QVBoxLayout()
        layout.addWidget(self.button_record)
        layout.addWidget(self.button_input)
        self.setLayout(layout)

    def toggle_recording(self):
        """Avvia o ferma la registrazione"""
        if not self.is_recording:
            print("[UI] Avviando la registrazione...")
            FastChainManager.run_action("START_CAPTURE_SPEECH")
            self.button_record.setText("Stop Registrazione")
            self.is_recording = True
        else:
            print("[UI] Fermando la registrazione...")
            text = FastChainManager.run_action("STOP_CAPTURE_SPEECH")
            print(f"[DEBUG] Testo acquisito: {text}")
            self.button_record.setText("Avvia Registrazione")
            self.is_recording = False

    def get_user_input(self):
        """Esegue l'azione per l'input da tastiera"""
        FastChainManager.run_action("GET_KEYBOARD_INPUT")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())
