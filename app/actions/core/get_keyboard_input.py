# FastChain
from fastchain.core import Action

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QLabel,
    QDialogButtonBox,
    QInputDialog,
)


# Dialogo custom che genera i campi in base alla lista degli input specificati
class DynamicInputDialog(QDialog):
    def __init__(self, inputs_spec, parent=None):
        """
        inputs_spec: lista di dizionari. Ogni dizionario DEVE contenere almeno il campo 'name'
          e può opzionalmente specificare:
            - title: Titolo del campo (default: stesso valore di 'name')
            - description: Testo guida (default: "")
            - size: "small", "medium" o "large" (default: "small")
        """
        super(DynamicInputDialog, self).__init__(parent)
        self.inputs_spec = inputs_spec
        self.widgets = {}  # mappa nome_campo -> widget
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        fixed_width = 400  # larghezza fissa per tutti i campi

        # Crea un widget per ciascun input in ordine verticale
        for field in self.inputs_spec:
            field_name = field.get("name")
            if not field_name:
                continue  # ignora se manca il nome
            field_title = field.get("title", field_name)
            description = field.get("description", "")
            size = field.get("size", "small").lower()

            # Crea l'etichetta per il campo
            label = QLabel(f"{field_title}: {description}")
            label.setFixedWidth(fixed_width)

            # Scegli il widget in base alla dimensione
            if size == "small":
                widget = QLineEdit()
                widget.setFixedHeight(30)
            elif size == "medium":
                widget = QTextEdit()
                widget.setFixedHeight(100)
            elif size == "large":
                widget = QTextEdit()
                widget.setFixedHeight(200)
            else:
                widget = QLineEdit()
                widget.setFixedHeight(30)

            widget.setFixedWidth(fixed_width)

            # Disposizione verticale: etichetta sopra, widget sotto
            field_layout = QVBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(widget)
            main_layout.addLayout(field_layout)

            self.widgets[field_name] = widget

        # Aggiunge i bottoni Ok/Cancel in fondo
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_values(self):
        """Restituisce un dizionario con i valori inseriti, mappando field_name -> valore."""
        values = {}
        for name, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text()
            elif isinstance(widget, QTextEdit):
                values[name] = widget.toPlainText()
        return values


class GetKeyboardInputAction:
    def execute(self, params=None):
        """
        Acquisce uno o più input dall'utente tramite una UI dinamica.

        Parametri attesi nel dizionario 'params':
          - title: Titolo generale del dialogo (default: "Input Richiesto")
          - inputs: lista di dizionari, ognuno contenente:
                - name: identificatore dell'input (obbligatorio)
                - title: Titolo del campo (default: lo stesso del nome)
                - description: Testo guida per il campo (default: "")
                - size: "small", "medium" o "large" (default: "small")

        Se 'inputs' non viene fornito, viene usato un dialogo semplice.

        Ritorna un dizionario con i valori inseriti se l'utente conferma, altrimenti None.
        """
        params = params or {}
        dialog_title = params.get("title", "Input Richiesto")
        inputs_spec = params.get("inputs")

        # Fallback: se non viene fornita una lista di input, usa il dialogo standard di QInputDialog
        if not inputs_spec:
            text, ok = QInputDialog.getText(
                None, dialog_title, "- Digita il tuo comando:"
            )
            return text if ok else None

        # Crea il dialogo dinamico con la lista degli input
        dialog = DynamicInputDialog(inputs_spec)
        dialog.setWindowTitle(dialog_title)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_values()
        else:
            return None


GET_KEYBOARD_INPUT = Action(
    name="GET_KEYBOARD_INPUT",
    description="Acquisce uno o più input dall'utente tramite una UI dinamica.",
    verbose_name="Input da Tastiera Dinamico",
    core=True,
    steps=[
        {
            "function": GetKeyboardInputAction().execute,
            "input_type": dict,  # Si attende un dizionario come input
            "output_type": dict,  # Restituisce un dizionario con i valori inseriti
        }
    ],
    input_action=True,
)
