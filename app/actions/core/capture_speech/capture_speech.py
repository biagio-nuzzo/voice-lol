# PyQt
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

# Ui
from app.ui.ui import CaptureSpeechWorker


# Fastchain
from fastchain.core import Action


class CaptureSpeechAction:
    """Classe per avviare il riconoscimento vocale"""

    def __init__(self):
        self.thread = None
        self.worker = None

    def execute(self, _=None):
        """Esegue il riconoscimento vocale in un thread separato e restituisce il testo"""

        # Se un thread è già attivo, interromperlo prima di crearne uno nuovo
        self.stop()

        self.thread = QThread()
        self.worker = CaptureSpeechWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Avvia il thread
        self.thread.start()
        return "Registrazione vocale avviata..."

    def stop(self):
        """Ferma il thread senza chiudere tutta l'app"""
        if self.worker and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()  # Qui potrebbe esserci il problema
            self.thread.wait()

        # IMPORTANTE: Impedisci la chiusura della finestra principale
        if not QApplication.instance().activeWindow():
            print("Errore: il thread ha chiuso l'interfaccia, riaprendola...")
            main_window = QApplication.instance().topLevelWidgets()[
                0
            ]  # Riapre la UI se chiusa
            main_window.show()

    def handle_finished(self, result):
        """Gestisce la fine della registrazione e stampa il risultato"""
        print("Registrazione completata:", result)


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
