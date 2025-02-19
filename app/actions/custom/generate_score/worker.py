# Built-in
import os
import random
import subprocess

# External
from PyQt5.QtCore import QObject, pyqtSignal

note_range = 8


class GenerateScoreWorker(QObject):
    finished = pyqtSignal(str, list)
    error = pyqtSignal(str)

    def __init__(self, notes, clef, include_sharps=False):
        super().__init__()
        self.notes = notes  # note inserite (non usate per la generazione)
        self.clef = clef  # "treble" o "bass"
        self.include_sharps = include_sharps
        print(
            "[Worker] Inizializzato con note:",
            self.notes,
            "chiave:",
            self.clef,
            "include_sharps:",
            self.include_sharps,
        )

    def run(self):
        try:
            print("[Worker] Avvio generazione spartito con LilyPond.")
            # Se l'opzione per i diesis è abilitata includiamo anche le versioni diesis (in notazione LilyPond),
            # altrimenti limitiamoci alle note naturali.
            if self.include_sharps:
                allowed_notes = [
                    "c",
                    "cis",
                    "d",
                    "dis",
                    "e",
                    "f",
                    "fis",
                    "g",
                    "gis",
                    "a",
                    "ais",
                    "b",
                ]
            else:
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
