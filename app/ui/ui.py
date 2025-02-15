# Built-in
import sys
import os

# PyQt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
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

# Emitting Stream
from app.ui.emit_stream import EmittingStream

# Costanti di configurazione
BACKGROUND_COLOR = "#505050"  # Sfondo principale
FONT_FAMILY = "'Segoe UI', sans-serif"
FONT_SIZE = "12pt"
BUTTON_BG_COLOR = "#222324"
BUTTON_HOVER_COLOR = "#1b1c1d"
TEXTEDIT_BG_COLOR = "#353535"
TEXTEDIT_TEXT_COLOR = "#e0e0e0"
SCROLLBAR_BG_COLOR = "#2e2e2e"
SCROLLBAR_HANDLE_COLOR = "#555555"
SCROLLBAR_HANDLE_HOVER_COLOR = "#777777"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GIF_OPACITY_INACTIVE = 0.2
GIF_OPACITY_ACTIVE = 1.0
GIF_RELATIVE_PATH = os.path.join("assets", "recording.gif")


class MainUI(QWidget):
    """
    Interfaccia principale dell'applicazione.
    """

    def __init__(self):
        super().__init__()
        self.controller = CaptureSpeechSingleton.get_controller()
        self.setup_stylesheet()
        self.setup_components()
        self.setup_layout()
        self.setup_redirect()
        self.setup_timer()
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Registratore Vocale")

    def setup_stylesheet(self):
        """
        Configura lo stylesheet globale dell'interfaccia.
        """
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {BACKGROUND_COLOR};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE};
            }}
            QPushButton {{
                background-color: {BUTTON_BG_COLOR};
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
            QTextEdit {{
                background-color: {TEXTEDIT_BG_COLOR};
                color: {TEXTEDIT_TEXT_COLOR};
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
            }}
            /* Personalizzazione della scrollbar verticale per QTextEdit */
            QTextEdit QScrollBar:vertical {{
                background: {SCROLLBAR_BG_COLOR};
                width: 8px;
                margin: 0px;
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: {SCROLLBAR_HANDLE_COLOR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: {SCROLLBAR_HANDLE_HOVER_COLOR};
            }}
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {{
                background: none;
            }}
            QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
        )

    def setup_components(self):
        """
        Crea e configura i componenti dell'interfaccia.
        """
        # Pulsante di registrazione
        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.toggle_recording)

        # Creazione del QLabel per la gif
        self.label_gif = QLabel(self)
        # Costruzione del percorso assoluto della gif
        current_dir = os.path.dirname(os.path.realpath(__file__))
        gif_path = os.path.join(current_dir, GIF_RELATIVE_PATH)
        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print("La gif non è stata caricata correttamente:", gif_path)
        self.label_gif.setMovie(self.movie)
        # Avvio della gif per mostrare il primo frame, quindi pausa
        self.movie.start()
        self.movie.setPaused(True)
        # Impostazione dell'effetto opacità per la gif
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(GIF_OPACITY_INACTIVE)
        self.label_gif.setGraphicsEffect(self.opacity_effect)

        # Terminale: QTextEdit per l'output
        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("Output del terminale...")

    def setup_layout(self):
        """
        Organizza i componenti in layout.
        """
        # Layout orizzontale per il pulsante e la gif
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.button_record)
        h_layout.addWidget(self.label_gif)

        # Layout principale con il terminale sotto
        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.console_output)
        self.setLayout(main_layout)

    def setup_redirect(self):
        """
        Reindirizza stdout e stderr verso il QTextEdit.
        """
        self.stdout_stream = EmittingStream()
        self.stdout_stream.textWritten.connect(self.append_console_text)
        sys.stdout = self.stdout_stream
        sys.stderr = self.stdout_stream

    def setup_timer(self):
        """
        Configura un timer per aggiornare periodicamente lo stato dell'interfaccia.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_state)
        self.timer.start(500)

    def append_console_text(self, text):
        """
        Aggiunge il testo al QTextEdit del terminale.
        """
        self.console_output.moveCursor(self.console_output.textCursor().End)
        self.console_output.insertPlainText(text)
        self.console_output.moveCursor(self.console_output.textCursor().End)

    def toggle_recording(self):
        """
        Gestisce l'avvio e l'arresto della registrazione.
        """
        if state["recording"]:
            self.controller.stop_capture()
        else:
            self.controller.start_capture("PRINT_VALUE")

    def update_ui_state(self):
        """
        Aggiorna lo stato della UI (testo del pulsante, animazione e opacità della gif)
        in base allo stato di registrazione.
        """
        if state["recording"]:
            self.button_record.setText("Stop Registrazione")
            if self.movie.state() != QMovie.Running:
                self.movie.start()
            self.movie.setPaused(False)
            self.opacity_effect.setOpacity(GIF_OPACITY_ACTIVE)
        else:
            self.button_record.setText("Avvia Registrazione")
            self.movie.setPaused(True)
            self.opacity_effect.setOpacity(GIF_OPACITY_INACTIVE)
