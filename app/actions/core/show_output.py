# FastChain
from fastchain.core import Action

# PyQt5
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    QFrame,
    QSizePolicy,
    QScrollArea,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


# Dialog per mostrare il testo di output in stile chat, con scroll verticale se necessario
class ShowOutputDialog(QDialog):
    def __init__(self, text, config, parent=None):
        """
        :param text: Testo da mostrare.
        :param config: Dizionario di configurazione del dialog.
                       Può contenere:
                         - title: Titolo del dialog (default: "Il tuo assistente virtuale dice: Ecco cosa ho da dirti")
                         - size: "small", "medium" o "large" (default: "small")
        """
        super(ShowOutputDialog, self).__init__(parent)
        self.text = text
        self.config = config
        self.init_ui()

    def init_ui(self):
        # Mappatura delle taglie in dimensioni
        size = self.config.get("size", "small").lower()
        if size == "small":
            width, height = 400, 250
        elif size == "medium":
            width, height = 500, 350
        elif size == "large":
            width, height = 600, 450
        else:
            width, height = 400, 250

        default_title = "Il tuo assistente virtuale dice: Ecco cosa ho da dirti"
        title = self.config.get("title", default_title)
        self.setWindowTitle(title)
        self.resize(width, height)

        # Layout principale con margini e spaziatura definiti
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header: titolo con personalità, allineato a sinistra
        header_label = QLabel(title)
        header_font = QFont("Helvetica", 14, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(header_label)

        # Riquadro in stile chat per il messaggio (senza bordi visibili)
        message_frame = QFrame()
        message_frame.setStyleSheet(
            """
            QFrame {
                background-color: #2d2d2d;
                border: none;
                border-radius: 8px;
            }
        """
        )
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(15, 15, 15, 15)

        # Testo dell'output: allineato in alto a sinistra
        output_label = QLabel(self.text)
        output_label.setStyleSheet("color: #e0e0e0;")
        output_label.setFont(QFont("Consolas", 11))
        output_label.setWordWrap(True)
        output_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        output_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        message_layout.addWidget(output_label)

        # Inseriamo il riquadro del messaggio in una QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(message_frame)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll_area)

        # Bottone "Chiudi" posizionato in basso a destra
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_button = button_box.button(QDialogButtonBox.Close)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #222324;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1b1c1d;
            }
        """
        )
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(button_box, alignment=Qt.AlignRight)


# Action per mostrare il dialog di output
class ShowOutputDialogAction:
    def execute(self, params=None):
        """
        Mostra un dialog contenente un testo di output e attende la chiusura tramite il pulsante.

        Parametri attesi nel dizionario 'params':
          - text: (obbligatorio) la stringa da visualizzare.
          - config: (opzionale) dizionario di configurazione per il dialog.
                    Esempio:
                        {
                            "title": "Il tuo assistente virtuale dice: Ecco cosa ho da dirti",
                            "size": "medium"
                        }

        Ritorna un dizionario con l'output visualizzato se l'utente chiude il dialog.
        """
        params = params or {}
        text = params.get("text")
        if text is None:
            raise ValueError("Il parametro 'text' è obbligatorio.")
        config = params.get("config", {})
        dialog = ShowOutputDialog(text, config)
        dialog.exec_()
        return {"output": text}


SHOW_OUTPUT = Action(
    name="SHOW_OUTPUT",
    description="Mostra un testo in un dialog configurabile con taglie 'small', 'medium' o 'large', in stile chat con scroll verticale se necessario.",
    verbose_name="Output Dialog",
    core=True,
    steps=[
        {
            "function": ShowOutputDialogAction().execute,
            "input_type": dict,  # Si attende un dizionario in input
            "output_type": dict,  # Restituisce un dizionario
        }
    ],
    input_action=True,
)
