# main_ui.py
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QPushButton
from PyQt5.QtCore import QTimer
from app.ui.global_states import state  # Importa il dizionario globale
from app.actions.core.capture_speech.capture_speech import CaptureSpeechSingleton
from fastchain.manager import FastChainManager


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")
        self.controller = CaptureSpeechSingleton.get_controller()

        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.toggle_recording)

        self.test_button = QPushButton("Test Button", self)
        self.test_button.clicked.connect(self.test_auto_start_capture)

        layout = QVBoxLayout()
        layout.addWidget(self.button_record)
        layout.addWidget(self.test_button)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_button_text)
        self.timer.start(500)

    def toggle_recording(self):
        if state["recording"]:
            self.controller.stop_capture()
        else:
            self.controller.start_capture()

    def test_auto_start_capture(self):
        """Avvia automaticamente la registrazione usando AUTO_START_CAPTURE"""
        FastChainManager.run_action("AUTO_START_CAPTURE")

    def update_button_text(self):
        # Usa lo stato globale per aggiornare il testo del pulsante
        print("[UI] Aggiornamento bottone: state['recording'] =", state["recording"])
        if state["recording"]:
            self.button_record.setText("Stop Registrazione")
        else:
            self.button_record.setText("Avvia Registrazione")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())
