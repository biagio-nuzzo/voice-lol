from PyQt5.QtWidgets import QApplication
from FastChain.core import Action
from ui import SpeechRecognitionDialog, SpeechRecognitionManager


class CaptureSpeechAction:
    """Classe per avviare il riconoscimento vocale"""

    def __init__(self):
        self.recognition_manager = SpeechRecognitionManager()

    def execute(self, _=None):
        """Esegue il riconoscimento vocale e restituisce il testo acquisito."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        dialog = SpeechRecognitionDialog(self.recognition_manager)
        dialog.exec_()

        return (
            dialog.full_text.strip()
            if dialog.full_text
            else "Nessun input vocale ricevuto"
        )


CAPTURE_SPEECH_ACTION = Action(
    name="CAPTURE_SPEECH",
    description="Registra l'audio dell'utente e lo converte in testo mostrando una finestra di dialogo.",
    verbose_name="Registrazione Vocale",
    steps=[
        {
            "function": CaptureSpeechAction().execute,
            "input_type": None,
            "output_type": str,
        }
    ],
    input_action=True,
)
