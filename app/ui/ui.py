# Built-in
import sys
import os

# PyQt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QApplication,
    QPushButton,
    QTextEdit,
    QLabel,
    QGraphicsOpacityEffect,
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QTimer

# Global States
from app.ui.global_states import state

# Actions
from app.actions.core.capture_speech.capture_speech_controller import (
    CaptureSpeechSingleton,
)

# APPOGGIATO
# emitting_stream.py
from PyQt5.QtCore import QObject, pyqtSignal


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupRedirect()

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")
        # Impostiamo uno sfondo chiaro per la finestra
        self.setStyleSheet("background-color: #f0f0f0;")
        self.controller = CaptureSpeechSingleton.get_controller()

        # Pulsante con colore scuro e testo bianco (non troppo aggressivo)
        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.setStyleSheet(
            "background-color: #444444; color: white; padding: 8px 16px; border: none;"
        )
        self.button_record.clicked.connect(self.toggle_recording)

        # Creiamo il QLabel per la gif
        self.label_gif = QLabel(self)
        # Costruiamo il percorso assoluto della gif
        current_dir = os.path.dirname(os.path.realpath(__file__))
        gif_path = os.path.join(current_dir, "assets", "recording.gif")
        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print("La gif non è stata caricata correttamente:", gif_path)
        self.label_gif.setMovie(self.movie)
        # Avviamo la gif e la mettiamo subito in pausa, in modo da mostrare il primo frame
        self.movie.start()
        self.movie.setPaused(True)
        # Impostiamo l'effetto opacità iniziale (opaca al 50% quando la registrazione è disattivata)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.5)
        self.label_gif.setGraphicsEffect(self.opacity_effect)

        # Terminale: sfondo nero, testo bianco
        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("Output del terminale...")
        self.console_output.setStyleSheet("background-color: black; color: white;")

        # Layout orizzontale per il pulsante e la gif
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.button_record)
        h_layout.addWidget(self.label_gif)

        # Layout principale
        layout = QVBoxLayout()
        layout.addLayout(h_layout)
        layout.addWidget(self.console_output)
        self.setLayout(layout)

        # Impostiamo dimensioni maggiori per la finestra
        self.resize(800, 600)

        # Timer per aggiornare lo stato della UI in base a state["recording"]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_state)
        self.timer.start(500)

    def setupRedirect(self):
        self.stdout_stream = EmittingStream()
        self.stdout_stream.textWritten.connect(self.appendConsoleText)
        sys.stdout = self.stdout_stream
        sys.stderr = self.stdout_stream

    def appendConsoleText(self, text):
        self.console_output.moveCursor(self.console_output.textCursor().End)
        self.console_output.insertPlainText(text)
        self.console_output.moveCursor(self.console_output.textCursor().End)

    def toggle_recording(self):
        if state["recording"]:
            self.controller.stop_capture()
        else:
            self.controller.start_capture("PRINT_VALUE")

    def update_ui_state(self):
        if state["recording"]:
            self.button_record.setText("Stop Registrazione")
            # Se la registrazione è attiva, assicuriamoci che la gif non sia in pausa e imposta opacità completa
            if self.movie.state() != QMovie.Running:
                self.movie.start()
            self.movie.setPaused(False)
            self.opacity_effect.setOpacity(1.0)
        else:
            self.button_record.setText("Avvia Registrazione")
            # Se la registrazione è disattivata, mettiamo in pausa la gif in modo che il frame corrente rimanga visibile
            self.movie.setPaused(True)
            self.opacity_effect.setOpacity(0.5)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec_())
