# PyQt
from PyQt5.QtCore import Qt, QThread, QSize, QRegExp
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
)
from PyQt5.QtGui import QPixmap, QRegExpValidator

# Actions
from app.actions.custom.generate_score.worker import GenerateScoreWorker
from app.actions.custom.generate_score.piano_widget import PianoWidget

note_range = 8

# Costanti per lo stile dei tasti in modalità "computer" (non usati per il pianoforte grafico)
DEFAULT_KEY_STYLE = "border: 1px solid #444; background-color: #808080;"
PRESSED_KEY_STYLE = "border: 1px solid #444; background-color: #A0A0A0;"


class GenerateScoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[Dialog] Inizializzazione del dialog.")
        self.setWindowTitle("Genera Spartito")
        self.thread = None
        self.worker = None
        self.correct_notes = None  # Note corrette generate dal worker
        self.current_input_index = 0  # Per gestire la posizione in modalità pianoforte
        self.init_ui()
        self.adjustSize()  # La finestra si adatta al contenuto

    def init_ui(self):
        print("[Dialog] Costruzione dell'interfaccia...")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Layout per gli input delle note (disposti in una griglia)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        self.note_edits = []
        validator = QRegExpValidator(QRegExp("^[a-gA-G#]$"))
        for i in range(note_range):
            label = QLabel(f"Nota {i+1}")
            label.setAlignment(Qt.AlignCenter)
            line_edit = QLineEdit()
            line_edit.setMaxLength(2)
            line_edit.setFixedWidth(50)
            line_edit.setValidator(validator)
            line_edit.textChanged.connect(
                lambda text, index=i: self.move_focus(text, index)
            )
            grid_layout.addWidget(label, 0, i)
            grid_layout.addWidget(line_edit, 1, i)
            self.note_edits.append(line_edit)
        main_layout.addLayout(grid_layout)

        # Layout per la selezione della chiave (Violino o Basso)
        clef_layout = QHBoxLayout()
        clef_label = QLabel("Seleziona chiave:")
        clef_layout.addWidget(clef_label)
        self.radio_treble = QRadioButton("Violino")
        self.radio_bass = QRadioButton("Basso")
        self.radio_treble.setChecked(True)
        clef_layout.addWidget(self.radio_treble)
        clef_layout.addWidget(self.radio_bass)
        # Raggruppamento radio button per la chiave
        self.clef_group = QButtonGroup(self)
        self.clef_group.addButton(self.radio_treble)
        self.clef_group.addButton(self.radio_bass)
        main_layout.addLayout(clef_layout)

        # Layout per la selezione della modalità di input
        input_mode_layout = QHBoxLayout()
        input_mode_label = QLabel("Modalità di input:")
        input_mode_layout.addWidget(input_mode_label)
        self.radio_computer = QRadioButton("Tastiera del computer")
        self.radio_piano = QRadioButton("Pianoforte")
        self.radio_computer.setChecked(True)  # Modalità di default
        input_mode_layout.addWidget(self.radio_computer)
        input_mode_layout.addWidget(self.radio_piano)
        # Raggruppamento radio button per la modalità di input
        self.input_mode_group = QButtonGroup(self)
        self.input_mode_group.addButton(self.radio_computer)
        self.input_mode_group.addButton(self.radio_piano)
        main_layout.addLayout(input_mode_layout)

        # Nuovo layout per l'abilitazione dei diesis
        sharps_layout = QHBoxLayout()
        self.sharps_checkbox = QCheckBox("Abilita diesis")
        self.sharps_checkbox.setChecked(False)
        sharps_layout.addWidget(self.sharps_checkbox)
        main_layout.addLayout(sharps_layout)

        # Collega il cambio di modalità per aggiornare l'interfaccia
        self.radio_computer.toggled.connect(self.update_input_mode)
        self.radio_piano.toggled.connect(self.update_input_mode)

        # Layout per il pianoforte grafico (visibile solo in modalità pianoforte)
        # Il widget viene centrato nell'interfaccia
        self.piano_keys_widget = PianoWidget()
        main_layout.addWidget(self.piano_keys_widget, alignment=Qt.AlignCenter)
        self.update_input_mode()  # Stato iniziale

        # Frame per visualizzare lo spartito generato
        self.score_frame = QFrame()
        self.score_frame.setFrameShape(QFrame.Box)
        score_layout = QVBoxLayout(self.score_frame)
        self.score_label = QLabel("Qui verrà visualizzato lo spartito")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setMinimumSize(500, 350)
        score_layout.addWidget(self.score_label)
        main_layout.addWidget(self.score_frame)

        # Label per mostrare il punteggio
        self.score_result_label = QLabel("")
        self.score_result_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.score_result_label)

        # Layout per i bottoni
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Genera Spartito")
        self.send_button = QPushButton("Invia Note")
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.send_button)
        main_layout.addLayout(button_layout)

        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)
        print("[Dialog] Interfaccia costruita con successo.")

    def update_input_mode(self):
        """Aggiorna l'interfaccia in base alla modalità di input selezionata."""
        if self.radio_piano.isChecked():
            for edit in self.note_edits:
                edit.setReadOnly(True)
            self.piano_keys_widget.show()
            self.current_input_index = 0
            if self.note_edits:
                self.note_edits[0].setFocus()
        else:
            for edit in self.note_edits:
                edit.setReadOnly(False)
            self.piano_keys_widget.hide()

    def move_focus(self, text, index):
        """
        In modalità tastiera, sposta il focus al campo successivo se è stato inserito un carattere;
        in modalità pianoforte il segnale viene ignorato.
        """
        if self.radio_piano.isChecked():
            return
        if len(text) > 0:
            if index < len(self.note_edits) - 1:
                self.note_edits[index + 1].setFocus()
            else:
                self.on_send_clicked()

    def illuminate_key(self, key):
        """Illumina il tasto bianco delegando al PianoWidget."""
        self.piano_keys_widget.illuminate_key(key)

    def illuminate_black_key(self, black_key):
        """Illumina il tasto nero delegando al PianoWidget."""
        self.piano_keys_widget.illuminate_black_key(black_key)

    def handle_piano_key(self, key):
        """
        Gestisce la pressione di un tasto bianco in modalità pianoforte:
        aggiorna l'input corrente e illumina il tasto.
        """
        if self.current_input_index >= note_range:
            return
        note_name, note_letter = self.piano_keys_widget.key_mapping[key]
        self.illuminate_key(key)
        self.note_edits[self.current_input_index].setText(note_letter.lower())
        if self.current_input_index < len(self.note_edits) - 1:
            self.current_input_index += 1
            self.note_edits[self.current_input_index].setFocus()
        else:
            self.on_send_clicked()

    def handle_black_key(self, key):
        """
        Gestisce la pressione di un tasto nero in modalità pianoforte:
        aggiorna l'input corrente e illumina il tasto.
        """
        if self.current_input_index >= note_range:
            return
        note_name, note_letter = self.piano_keys_widget.black_key_mapping[key]
        self.illuminate_black_key(note_letter)
        self.note_edits[self.current_input_index].setText(note_letter.lower())
        if self.current_input_index < len(self.note_edits) - 1:
            self.current_input_index += 1
            self.note_edits[self.current_input_index].setFocus()
        else:
            self.on_send_clicked()

    def keyPressEvent(self, event):
        """
        Se siamo in modalità pianoforte, intercettiamo le pressioni dei tasti fisici
        per inserire la nota corrispondente:
          - i tasti bianchi (a, s, d, f, g, h, j, k)
          - i tasti neri (w, r, t, u, i)
        """
        if self.radio_piano.isChecked():
            key = event.text().lower()
            if key in self.piano_keys_widget.key_mapping:
                self.handle_piano_key(key)
                return
            elif key in self.piano_keys_widget.black_key_mapping:
                self.handle_black_key(key)
                return
        super().keyPressEvent(event)

    def on_generate_clicked(self):
        print("[Dialog] Pulsante 'Genera Spartito' cliccato.")
        for edit in self.note_edits:
            edit.clear()
            edit.setStyleSheet("")
        self.score_result_label.setText("")
        self.correct_notes = None
        self.current_input_index = 0
        notes = [edit.text().strip() for edit in self.note_edits if edit.text().strip()]
        if not notes:
            print("[Dialog] Nessuna nota inserita, verranno generate note randomiche.")
        clef = "bass" if self.radio_bass.isChecked() else "treble"
        self.generate_button.setEnabled(False)
        self.score_label.setText("Generazione in corso...")
        self.thread = QThread()
        # Passiamo anche il valore del checkbox per includere o meno i diesis
        include_sharps = self.sharps_checkbox.isChecked()
        self.worker = GenerateScoreWorker(notes, clef, include_sharps)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        print("[Dialog] Avvio thread per generazione immagine.")
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_generation_finished(self, image_path, correct_notes):
        print("[Dialog] Generazione completata. Immagine salvata in:", image_path)
        self.correct_notes = correct_notes
        pixmap = QPixmap(image_path)
        target_size = QSize(500, 350)
        self.score_label.setPixmap(
            pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.generate_button.setEnabled(True)
        if self.note_edits:
            self.note_edits[0].setFocus()
            self.current_input_index = 0

    def on_generation_error(self, error_msg):
        print("[Dialog] Errore nella generazione:", error_msg)
        self.score_label.setText(
            "Errore nella generazione dello spartito:\n" + error_msg
        )
        self.generate_button.setEnabled(True)

    def on_send_clicked(self):
        print("[Dialog] Pulsante 'Invia Note' cliccato.")
        if self.correct_notes is None:
            self.score_result_label.setText("Genera prima lo spartito!")
            return

        user_notes = [edit.text().strip() for edit in self.note_edits]
        correct_count = 0
        for i, note in enumerate(user_notes):
            if (
                i < len(self.correct_notes)
                and note.lower() == self.correct_notes[i][0].lower()
            ):
                correct_count += 1
                self.note_edits[i].setStyleSheet("background-color: green;")
            else:
                self.note_edits[i].setStyleSheet("background-color: red;")
        self.score_result_label.setText(f"{correct_count}/{note_range}")

    def get_notes(self):
        notes = [edit.text() for edit in self.note_edits]
        print("[Dialog] Note inviate:", notes)
        return notes
