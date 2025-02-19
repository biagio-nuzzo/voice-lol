from fastchain.core import Action
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QRadioButton,
)
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QObject, QRegExp
import os
import subprocess
import random

note_range = 8


# Worker che genera lo spartito usando LilyPond
class GenerateScoreWorker(QObject):
    # Il segnale finished ora emette sia il percorso dell'immagine che le note corrette
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
            # Genera note randomiche con durata "4" senza ulteriori limitazioni
            random_notes = [
                random.choice(allowed_notes) + "4" for _ in range(note_range)
            ]
            print("[Worker] Note random generate:", random_notes)

            # Imposta il comando della chiave in base alla selezione
            if self.clef == "bass":
                clef_command = "\\clef bass"
            else:
                clef_command = "\\clef treble"

            # Costruisce il codice LilyPond usando le note random generate
            # Utilizziamo la stessa base relativa in entrambi i casi (c')
            lilypond_code = f"""
\\version "2.24.0"
\\relative c' {{
  {clef_command}
  \\key c \\major
  \\time 4/4
  {' '.join(random_notes)}
}}
"""

            # Calcola il percorso della cartella del file corrente e della cartella "tmp"
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tmp_dir = os.path.join(script_dir, "tmp")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
                print("[Worker] Cartella 'tmp' creata in:", tmp_dir)

            # Definisce i percorsi dei file all'interno della cartella tmp
            ly_file = os.path.join(tmp_dir, "spartito.ly")
            png_file = os.path.join(tmp_dir, "spartito.preview.png")

            # Scrive il file LilyPond nella cartella tmp
            with open(ly_file, "w") as f:
                f.write(lilypond_code)
            print("[Worker] File LilyPond scritto in:", ly_file)

            # Esegue LilyPond per generare il file PNG, impostando la cartella di lavoro su tmp_dir
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
        self.resize(500, 600)
        self.thread = None
        self.worker = None
        self.correct_notes = None  # Note corrette generate dal worker
        self.init_ui()

    def init_ui(self):
        print("[Dialog] Costruzione dell'interfaccia...")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Layout per gli input delle note
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        self.note_edits = []
        # Validator: accetta solo una lettera (a-g o A-G)
        validator = QRegExpValidator(QRegExp("^[a-gA-G]$"))
        for i in range(note_range):
            sub_layout = QVBoxLayout()
            sub_layout.setSpacing(2)
            label = QLabel(f"Nota {i+1}")
            line_edit = QLineEdit()
            line_edit.setMaxLength(1)
            line_edit.setFixedWidth(50)
            line_edit.setValidator(validator)
            sub_layout.addWidget(label)
            sub_layout.addWidget(line_edit)
            input_layout.addLayout(sub_layout)
            self.note_edits.append(line_edit)
        main_layout.addLayout(input_layout)

        # Layout per la selezione della chiave
        clef_layout = QHBoxLayout()
        clef_label = QLabel("Seleziona chiave:")
        clef_layout.addWidget(clef_label)
        self.radio_treble = QRadioButton("Violino")
        self.radio_bass = QRadioButton("Basso")
        self.radio_treble.setChecked(True)
        clef_layout.addWidget(self.radio_treble)
        clef_layout.addWidget(self.radio_bass)
        main_layout.addLayout(clef_layout)

        # Frame per visualizzare lo spartito generato
        self.score_frame = QFrame()
        self.score_frame.setFrameShape(QFrame.Box)
        score_layout = QVBoxLayout(self.score_frame)
        self.score_label = QLabel("Qui verrà visualizzato lo spartito")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setMinimumSize(800, 400)
        score_layout.addWidget(self.score_label)
        main_layout.addWidget(self.score_frame)

        # Label per mostrare il punteggio (es. "3/8")
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

    def on_generate_clicked(self):
        print("[Dialog] Pulsante 'Genera Spartito' cliccato.")
        # Reset degli input e dello score
        for edit in self.note_edits:
            edit.clear()
            edit.setStyleSheet("")
        self.score_result_label.setText("")
        self.correct_notes = None

        # Legge le note eventualmente inserite (non usate dal worker) e la scelta della chiave
        notes = [edit.text().strip() for edit in self.note_edits if edit.text().strip()]
        if not notes:
            print("[Dialog] Nessuna nota inserita, verranno generate note randomiche.")
        # Determina la chiave in base ai radio button
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
        target_size = QSize(800, 400)
        self.score_label.setPixmap(
            pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.generate_button.setEnabled(True)

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

        # Confronta le note inserite (solo la lettera) con quelle corrette
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
