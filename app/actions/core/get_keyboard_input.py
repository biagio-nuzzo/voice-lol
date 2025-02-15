# FastChain
from fastchain.core import Action

# PyQt
from PyQt5.QtWidgets import QInputDialog


class GetKeyboardInputAction:
    def execute(self, _=None):
        """
        Acquisisce l'input da tastiera dell'utente usando una finestra di dialogo non bloccante.
        """
        text, ok = QInputDialog.getText(
            None, "Input Richiesto", "- Digita il tuo comando:"
        )
        return text if ok else None


GET_KEYBOARD_INPUT = Action(
    name="GET_KEYBOARD_INPUT",
    description="Acquisisce un input dall'utente via tastiera e lo restituisce.",
    verbose_name="Input da Tastiera",
    steps=[
        {
            "function": GetKeyboardInputAction().execute,
            "input_type": None,
            "output_type": str,
        }
    ],
    input_action=True,
)
