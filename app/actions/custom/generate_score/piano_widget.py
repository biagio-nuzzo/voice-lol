# PyQt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtSvg import QSvgWidget

# Python
import os


# Percorsi delle immagini dei tasti del pianoforte (asset SVG)
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
WHITE_KEY = os.path.join(assets_dir, "white_key.svg")
WHITE_KEY_PRESSED = os.path.join(assets_dir, "white_key_pressed.svg")
BLACK_KEY = os.path.join(assets_dir, "black_key.svg")
BLACK_KEY_PRESSED = os.path.join(assets_dir, "black_key_pressed.svg")


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
