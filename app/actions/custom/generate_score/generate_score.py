# FastChain
from fastchain.core import Action

# PyQt
from PyQt5.QtWidgets import (
    QDialog,
)

# Actions
from app.actions.custom.generate_score.generate_dialog import GenerateScoreDialog


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


LETTURA_NOTE_MUSICALI = Action(
    name="LETTURA_NOTE_MUSICALI",
    description="""
    Apre un dialog per inserire note e scegliere la chiave (Violino o Basso),
    genera una battuta con LilyPond e invia le note. 
    L'azione è pensata per esercitarsi a riconoscere le note musicali.
    L'azione può essere richiesta dall'utente dicendo:
    "Inizia lettura note musicali"
    "Apri esercizio lettura note musicali"
    "Esercitazione lettura note musicali"
    "Esercitiamoci con le note musicali"
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
