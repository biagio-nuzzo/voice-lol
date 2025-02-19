from fastchain.core import Action
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
    QWidget,
    QButtonGroup,
)
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QObject, QRegExp, QTimer
from PyQt5.QtSvg import QSvgWidget
import os
import subprocess
import random

note_range = 8

# Percorsi delle immagini dei tasti del pianoforte (asset SVG)
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
WHITE_KEY = os.path.join(assets_dir, "white_key.svg")
WHITE_KEY_PRESSED = os.path.join(assets_dir, "white_key_pressed.svg")
BLACK_KEY = os.path.join(assets_dir, "black_key.svg")
BLACK_KEY_PRESSED = os.path.join(assets_dir, "black_key_pressed.svg")

# Costanti per lo stile dei tasti in modalità "computer" (non usati per il pianoforte grafico)
DEFAULT_KEY_STYLE = "border: 1px solid #444; background-color: #808080;"
PRESSED_KEY_STYLE = "border: 1px solid #444; background-color: #A0A0A0;"

# ------------------------------------------------------------------------------
# Widget PianoWidget: compone il pianoforte assemblando gli asset SVG
# ------------------------------------------------------------------------------


class PianoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Dimensioni dei tasti (in pixel)
        self.white_key_width = 40
        self.white_key_height = 150
        self.black_key_width = 24
        self.black_key_height = 90
        # Una ottava da LA a LA: 8 tasti bianchi
        self.octave_white_keys = 8

        # Imposta la dimensione fissa del widget
        self.setFixedSize(
            self.white_key_width * self.octave_white_keys, self.white_key_height
        )

        # Mappatura dei tasti bianchi (da LA a LA)
        # La disposizione sarà: "a" -> La, "s" -> Si, "d" -> Do, "f" -> Re, "g" -> Mi, "h" -> Fa, "j" -> Sol, "k" -> La
        self.key_mapping = {
            "a": ("La", "a"),
            "s": ("Si", "b"),
            "d": ("Do", "c"),
            "f": ("Re", "d"),
            "g": ("Mi", "e"),
            "h": ("Fa", "f"),
            "j": ("Sol", "g"),
            "k": ("La", "a"),
        }

        # Mappatura dei tasti neri
        # Associa i tasti fisici: w = La diesis, r = Do diesis, t = Re diesis, u = Fa diesis, i = Sol diesis
        self.black_key_mapping = {
            "w": ("La diesis", "a#"),
            "r": ("Do diesis", "c#"),
            "t": ("Re diesis", "d#"),
            "u": ("Fa diesis", "f#"),
            "i": ("Sol diesis", "g#"),
        }

        # Creazione dei tasti bianchi
        self.white_keys = {}
        physical_keys = ["a", "s", "d", "f", "g", "h", "j", "k"]
        for i, key in enumerate(physical_keys):
            white_key = QSvgWidget(WHITE_KEY, self)
            white_key.setGeometry(
                i * self.white_key_width, 0, self.white_key_width, self.white_key_height
            )
            self.white_keys[key] = white_key

        # Creazione dei tasti neri.
        # In un'ottava da LA a LA, i tasti neri sono:
        # - tra LA e SI: A#
        # - tra DO e RE: C#
        # - tra RE e MI: D#
        # - tra FA e SOL: F#
        # - tra SOL e LA: G#
        self.black_keys = {}
        black_key_positions = {
            "a#": 0,  # tra il tasto 0 (La) e il tasto 1 (Si)
            "c#": 2,  # tra il tasto 2 (Do) e il tasto 3 (Re)
            "d#": 3,  # tra il tasto 3 (Re) e il tasto 4 (Mi)
            "f#": 5,  # tra il tasto 5 (Fa) e il tasto 6 (Sol)
            "g#": 6,  # tra il tasto 6 (Sol) e il tasto 7 (La)
        }
        for note, white_index in black_key_positions.items():
            x = (white_index + 1) * self.white_key_width - self.black_key_width // 2
            black_key = QSvgWidget(BLACK_KEY, self)
            black_key.setGeometry(x, 0, self.black_key_width, self.black_key_height)
            self.black_keys[note] = black_key

    def illuminate_key(self, physical_key):
        """
        Illumina il tasto bianco corrispondente simulando la pressione:
        passa dalla versione normale a quella "premuta" per 200ms.
        """
        if physical_key in self.white_keys:
            key_widget = self.white_keys[physical_key]
            key_widget.load(WHITE_KEY_PRESSED)
            QTimer.singleShot(200, lambda: key_widget.load(WHITE_KEY))

    def illuminate_black_key(self, black_key):
        """
        Illumina il tasto nero corrispondente simulando la pressione:
        passa dalla versione normale a quella "premuta" per 200ms.
        """
        if black_key in self.black_keys:
            key_widget = self.black_keys[black_key]
            key_widget.load(BLACK_KEY_PRESSED)
            QTimer.singleShot(200, lambda: key_widget.load(BLACK_KEY))


# ------------------------------------------------------------------------------


# Worker che genera lo spartito usando LilyPond
class GenerateScoreWorker(QObject):
    finished = pyqtSignal(str, list)
    error = pyqtSignal(str)

    def __init__(self, notes, clef):
        super().__init__()
        self.notes = notes  # note inserite (non usate per la generazione)
        self.clef = clef  # "treble" o "bass"
        print("[Worker] Inizializzato con note:", self.notes, "e chiave:", self.clef)

    def run(self):
        try:
            print("[Worker] Avvio generazione spartito con LilyPond.")
            allowed_notes = ["c", "d", "e", "f", "g", "a", "b"]
            random_notes = [
                random.choice(allowed_notes) + "4" for _ in range(note_range)
            ]
            print("[Worker] Note random generate:", random_notes)

            if self.clef == "bass":
                clef_command = "\\clef bass"
                relative_mode = "\\relative c {"
            else:
                clef_command = "\\clef treble"
                relative_mode = "\\relative c'' {"

            lilypond_code = f"""
                \\version "2.24.0"
                {relative_mode}
                {clef_command}
                \\key c \\major
                \\time 4/4
                {' '.join(random_notes)}
                }}
                """

            script_dir = os.path.dirname(os.path.abspath(__file__))
            tmp_dir = os.path.join(script_dir, "tmp")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
                print("[Worker] Cartella 'tmp' creata in:", tmp_dir)

            ly_file = os.path.join(tmp_dir, "spartito.ly")
            png_file = os.path.join(tmp_dir, "spartito.preview.png")

            with open(ly_file, "w") as f:
                f.write(lilypond_code)
            print("[Worker] File LilyPond scritto in:", ly_file)

            result = subprocess.run(
                ["lilypond", "--png", "-dpreview", "-dresolution=300", ly_file],
                capture_output=True,
                text=True,
                check=True,
                cwd=tmp_dir,
            )
            print("[Worker] Output di LilyPond:", result.stdout, result.stderr)

            if not os.path.exists(png_file):
                raise Exception("Il file PNG non è stato creato.")

            print("[Worker] Spartito generato con successo in:", png_file)
            self.finished.emit(png_file, random_notes)
        except Exception as e:
            print("[Worker] Errore durante la generazione:", e)
            self.error.emit(str(e))


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
        self.worker = GenerateScoreWorker(notes, clef)
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


class GenerateScoreAction:
    def execute(self, params=None):
        print("[Action] Esecuzione di GenerateScoreAction...")
        dialog = GenerateScoreDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            notes = dialog.get_notes()
            print("[Action] Dialog accettato. Note:", notes)
            return {"notes": notes}
        else:
            print("[Action] Dialog annullato.")
            return None


GENERATE_SCORE = Action(
    name="GENERATE_SCORE",
    description="""
    Apre un dialog per inserire note e scegliere la chiave (Violino o Basso),
    genera una battuta con LilyPond e invia le note. 
    L'azione è pensata per esercitarsi a riconoscere le note musicali.
    """,
    verbose_name="Genera Spartito",
    steps=[
        {
            "function": GenerateScoreAction().execute,
            "input_type": None,
            "output_type": dict,
        }
    ],
    input_action=True,
)
