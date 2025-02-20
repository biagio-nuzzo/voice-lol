# PyQt
from PyQt5.QtCore import Qt, QThread, QSize, QRegExp, QEvent, QTimer
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
    QWidget,
)
from PyQt5.QtGui import QPixmap, QRegExpValidator

# Actions
from app.actions.custom.generate_score.worker import GenerateScoreWorker
from app.actions.custom.generate_score.piano_widget import PianoWidget

note_range = 8

DEFAULT_KEY_STYLE = "border: 1px solid #444; background-color: #808080;"
PRESSED_KEY_STYLE = "border: 1px solid #444; background-color: #A0A0A0;"


def convert_input(note):
    """
    Converte una nota inserita dall'utente (es. "d#")
    nella notazione usata dal worker (es. "dis").
    Se non contiene "#", restituisce la nota in minuscolo.
    """
    note = note.lower()
    mapping = {"c#": "cis", "d#": "dis", "f#": "fis", "g#": "gis", "a#": "ais"}
    return mapping.get(note, note)


# ---------------- TrainingWidget ----------------
class TrainingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_running = False
        self.exercise_scores = []
        self.elapsed_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        self.timer_label = QLabel("Tempo: 00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.stats_label = QLabel("Esercizi: 0 | Media: 0.00")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.session_button = QPushButton("Avvia Sessione")
        self.session_button.clicked.connect(self.toggle_session)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.session_button)

    def toggle_session(self):
        if self.session_running:
            self.session_running = False
            self.timer.stop()
            self.session_button.setText("Avvia Sessione")
        else:
            self.session_running = True
            self.exercise_scores = []
            self.elapsed_seconds = 0
            self.timer.start(1000)
            self.session_button.setText("Ferma Sessione")
            self.update_stats()

    def update_timer(self):
        self.elapsed_seconds += 1
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.timer_label.setText(f"Tempo: {minutes:02d}:{seconds:02d}")

    def add_score(self, score):
        self.exercise_scores.append(score)
        self.update_stats()

    def update_stats(self):
        count = len(self.exercise_scores)
        average = sum(self.exercise_scores) / count if count > 0 else 0
        self.stats_label.setText(f"Esercizi: {count} | Media: {average:.2f}")


# ------------- GenerateScoreDialog (UI principale) -------------
class GenerateScoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[Dialog] Inizializzazione del dialog.")
        self.setWindowTitle("Genera Spartito")
        self.thread = None
        self.worker = None
        self.correct_notes = None  # Note corrette generate dal worker
        self.current_input_index = 0  # Indice dell'input attivo (modalità pianoforte)
        self.init_ui()
        self.adjustSize()

    def init_ui(self):
        print("[Dialog] Costruzione dell'interfaccia...")
        # Layout principale: due colonne (30% sinistra, 70% destra)
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --------- Colonna sinistra: Widget Settings e Widget Training ---------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # ----- Widget Settings -----
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(10)
        # (Qui inserisci il codice per impostare il widget settings, come nel codice precedente)
        # Ad esempio:
        input_mode_label = QLabel("Modalità di input:")
        self.radio_computer = QRadioButton("Tastiera del computer")
        self.radio_piano = QRadioButton("Pianoforte")
        self.radio_computer.setChecked(True)
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(input_mode_label)
        mode_layout.addWidget(self.radio_computer)
        mode_layout.addWidget(self.radio_piano)
        self.input_mode_group = QButtonGroup(self)
        self.input_mode_group.addButton(self.radio_computer)
        self.input_mode_group.addButton(self.radio_piano)
        settings_layout.addLayout(mode_layout)

        # Selezione chiave
        clef_label = QLabel("Seleziona chiave:")
        self.radio_treble = QRadioButton("Violino")
        self.radio_bass = QRadioButton("Basso")
        self.radio_treble.setChecked(True)
        clef_layout = QVBoxLayout()
        clef_layout.addWidget(clef_label)
        clef_layout.addWidget(self.radio_treble)
        clef_layout.addWidget(self.radio_bass)
        self.clef_group = QButtonGroup(self)
        self.clef_group.addButton(self.radio_treble)
        self.clef_group.addButton(self.radio_bass)
        settings_layout.addLayout(clef_layout)

        # Abilita diesis
        self.sharps_checkbox = QCheckBox("Abilita diesis")
        self.sharps_checkbox.setChecked(False)
        settings_layout.addWidget(self.sharps_checkbox)

        # Collega aggiornamento modalità
        self.radio_computer.toggled.connect(self.update_input_mode)
        self.radio_piano.toggled.connect(self.update_input_mode)

        left_layout.addWidget(settings_widget, alignment=Qt.AlignTop)

        # ----- Widget Training (già definito) -----
        self.training_widget = TrainingWidget()
        left_layout.addWidget(self.training_widget, alignment=Qt.AlignTop)

        # --------- Colonna destra: Input Notes e Display Score ---------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # ----- Riga 1: Input Notes -----
        input_notes_widget = QWidget()
        input_notes_layout = QVBoxLayout(input_notes_widget)
        input_notes_layout.setSpacing(5)
        # Griglia per gli input delle note
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        self.note_edits = []
        validator = QRegExpValidator(QRegExp("^[a-gA-G](#)?$"))
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
            line_edit.textChanged.connect(self.check_all_filled)
            line_edit.installEventFilter(self)
            grid_layout.addWidget(label, 0, i)
            grid_layout.addWidget(line_edit, 1, i)
            self.note_edits.append(line_edit)
        input_notes_layout.addLayout(grid_layout)

        # (Opzionale) Pianoforte grafico: se in modalità pianoforte lo mostriamo
        self.piano_keys_widget = PianoWidget()
        input_notes_layout.addWidget(self.piano_keys_widget, alignment=Qt.AlignCenter)

        right_layout.addWidget(input_notes_widget)

        # ----- Riga 2: Display Score -----
        display_score_widget = QWidget()
        display_score_layout = QVBoxLayout(display_score_widget)
        display_score_layout.setSpacing(5)
        # Frame per lo spartito
        self.score_frame = QFrame()
        self.score_frame.setFrameShape(QFrame.Box)
        score_layout = QVBoxLayout(self.score_frame)
        self.score_label = QLabel("Qui verrà visualizzato lo spartito")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setMinimumSize(500, 350)
        score_layout.addWidget(self.score_label)
        display_score_layout.addWidget(self.score_frame)

        # Risultato dell'esercizio corrente
        self.score_result_label = QLabel("")
        self.score_result_label.setAlignment(Qt.AlignCenter)
        display_score_layout.addWidget(self.score_result_label)

        # Pulsanti: Genera Spartito, Invia Note e Reset Form
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Genera Spartito")
        self.send_button = QPushButton("Invia Note")
        self.reset_button = QPushButton("Reset Form")
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.reset_button)
        display_score_layout.addLayout(button_layout)

        right_layout.addWidget(display_score_widget)

        # Aggiungiamo le due colonne al layout principale con stretch (3:7)
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 7)

        # Collega i pulsanti
        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)

        # Modalità di input: gli input rimangono editabili
        self.update_input_mode()
        print("[Dialog] Interfaccia costruita con successo.")

    def keyPressEvent(self, event):
        # Se l'utente preme Enter in qualunque parte, simula "Invia Note"
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.on_send_clicked()
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            if obj in self.note_edits:
                self.current_input_index = self.note_edits.index(obj)
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Backspace and obj in self.note_edits:
                if obj.text() == "" and self.current_input_index > 0:
                    self.current_input_index -= 1
                    self.note_edits[self.current_input_index].setFocus()
                    return True
            if event.key() == Qt.Key_Left and obj in self.note_edits:
                idx = self.note_edits.index(obj)
                if idx > 0:
                    self.current_input_index = idx - 1
                    self.note_edits[self.current_input_index].setFocus()
                    return True
            if event.key() == Qt.Key_Right and obj in self.note_edits:
                idx = self.note_edits.index(obj)
                if idx < len(self.note_edits) - 1:
                    self.current_input_index = idx + 1
                    self.note_edits[self.current_input_index].setFocus()
                    return True
            if self.radio_piano.isChecked():
                key = event.text().lower()
                if key in self.piano_keys_widget.key_mapping:
                    self.handle_piano_key(key)
                    return True
                elif key in self.piano_keys_widget.black_key_mapping:
                    self.handle_black_key(key)
                    return True
        return super().eventFilter(obj, event)

    def update_input_mode(self):
        for edit in self.note_edits:
            edit.setReadOnly(False)
        if self.radio_piano.isChecked():
            self.piano_keys_widget.show()
            self.current_input_index = 0
            if self.note_edits:
                self.note_edits[0].setFocus()
        else:
            self.piano_keys_widget.hide()

    def move_focus(self, text, index):
        if self.radio_piano.isChecked():
            return
        if len(text) > 0:
            if index < len(self.note_edits) - 1:
                self.note_edits[index + 1].setFocus()
            else:
                self.on_send_clicked()

    def check_all_filled(self):
        if all(edit.text() != "" for edit in self.note_edits):
            self.on_send_clicked()

    def illuminate_key(self, key):
        self.piano_keys_widget.illuminate_key(key)

    def illuminate_black_key(self, black_key):
        self.piano_keys_widget.illuminate_black_key(black_key)

    def handle_piano_key(self, key):
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
            converted = convert_input(note)
            correct_note = self.correct_notes[i]
            if correct_note and correct_note[-1].isdigit():
                correct_note = correct_note[:-1]
            if converted == correct_note.lower():
                correct_count += 1
                self.note_edits[i].setStyleSheet("background-color: green;")
            else:
                self.note_edits[i].setStyleSheet("background-color: red;")
        self.score_result_label.setText(f"{correct_count}/{note_range}")
        # Se la sessione di allenamento è attiva, aggiungiamo il punteggio
        if self.training_widget.session_running:
            self.training_widget.add_score(correct_count)

    def on_reset_clicked(self):
        print("[Dialog] Pulsante 'Reset Form' cliccato.")
        for edit in self.note_edits:
            edit.clear()
            edit.setStyleSheet("")
        self.current_input_index = 0
        if self.note_edits:
            self.note_edits[0].setFocus()

    def get_notes(self):
        notes = [edit.text() for edit in self.note_edits]
        print("[Dialog] Note inviate:", notes)
        return notes
