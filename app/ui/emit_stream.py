# PyQt
from PyQt5.QtCore import QObject, pyqtSignal


class EmittingStream(QObject):
    """
    Classe per emettere il testo verso un segnale,
    utile per reindirizzare stdout/stderr al QTextEdit.
    """

    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass
