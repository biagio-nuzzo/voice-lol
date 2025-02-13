# Built-in
import sys
import os

# PyQt
from PyQt5.QtWidgets import QApplication

# UI
from app.ui.ui import MainUI

# Aggiungiamo il percorso della cartella principale per evitare ModuleNotFoundError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """Avvia l'applicazione FastChain - Voice Agent"""
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
