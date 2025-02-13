# PyQt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# UI Components
from app.ui.actions import ActionsPanel


class MainUI(QWidget):
    """Interfaccia principale con pulsanti per tutte le action"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastChain - Voice Agent")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.actions_panel = ActionsPanel()
        layout.addWidget(self.actions_panel)

        self.setLayout(layout)
