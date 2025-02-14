from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTextEdit, QInputDialog

# Actions
from actions.core.capture_speech.capture_speech import CAPTURE_SPEECH_ACTION
from actions.core.get_keyboard_input import (
    GET_KEYBOARD_INPUT_ACTION,
)  # Importiamo l'azione


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.recording_thread = None

    def initUI(self):
        self.setWindowTitle("Registratore Vocale")

        self.button_record = QPushButton("Avvia Registrazione", self)
        self.button_record.clicked.connect(self.toggle_recording)

        self.button_input = QPushButton("Inserisci Testo", self)  # Nuovo pulsante
        self.button_input.clicked.connect(self.get_keyboard_input)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.button_record)
        layout.addWidget(self.button_input)  # Aggiungiamo il nuovo pulsante
        layout.addWidget(self.text_display)
        self.setLayout(layout)

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.button_record.setText("Avvia Registrazione")
            self.recording_thread.stop()  # Ferma il thread di registrazione
        else:
            self.is_recording = True
            self.button_record.setText("Interrompi Registrazione")
            self.text_display.clear()  # Pulisce il testo precedente
            self.start_recording()

    def start_recording(self):
        self.recording_thread = CAPTURE_SPEECH_ACTION.execute()
        self.recording_thread.partial_result.connect(self.update_text_display)
        self.recording_thread.finished.connect(self.on_recording_finished)
        self.recording_thread.start()

    def update_text_display(self, text):
        current_text = self.text_display.toPlainText().strip()

        # Manteniamo un set delle parole già visualizzate
        displayed_words = set(current_text.split())
        new_words = text.split()

        # Filtriamo solo le parole che non sono già state stampate
        words_to_add = [word for word in new_words if word not in displayed_words]

        if words_to_add:
            updated_text = (
                current_text + " " + " ".join(words_to_add)
                if current_text
                else " ".join(words_to_add)
            )
            self.text_display.setPlainText(
                updated_text.strip()
            )  # Aggiorniamo il testo senza nuove righe

    def on_recording_finished(self, text):
        self.text_display.append(text)
        self.is_recording = False
        self.button_record.setText("Avvia Registrazione")

    def get_keyboard_input(self):
        """Esegue l'azione GET_KEYBOARD_INPUT_ACTION e aggiorna il testo nella UI."""
        text = GET_KEYBOARD_INPUT_ACTION.execute()
        if text:
            self.update_text_display(
                text
            )  # Aggiunge il testo inserito al riquadro di testo
