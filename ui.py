import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QLineEdit,
    QScrollArea,
    QFrame,
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont
from utils import (
    get_action_registry,
)  # 🔹 Importiamo la funzione per ottenere le action disponibili


class ActionLauncherApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configurazione finestra
        self.setWindowTitle("Action Launcher")
        self.setGeometry(300, 300, 800, 600)  # 🔹 Larghezza 800px, Altezza 600px

        # Layout principale orizzontale (Diviso in due sezioni: Pulsanti + Terminale)
        main_layout = QHBoxLayout()

        # **SEZIONE SINISTRA (30%) → LISTA DI ACTION SCROLLABILE**
        self.action_frame = QFrame()
        self.action_frame.setFixedWidth(240)  # 30% di 800px ≈ 240px
        self.action_layout = QVBoxLayout(self.action_frame)

        # **Pulsante per aggiornare la lista delle action**
        self.refresh_button = QPushButton("🔄 Aggiorna Azioni")
        self.refresh_button.setFont(QFont("Arial", 12))
        self.refresh_button.clicked.connect(self.refresh_action_buttons)
        self.action_layout.addWidget(
            self.refresh_button
        )  # 🔹 Aggiunto sopra i pulsanti

        # Scroll area per i pulsanti
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.action_frame)

        main_layout.addWidget(self.scroll_area)  # Aggiungiamo la lista azioni

        # **SEZIONE DESTRA (70%) → TERMINALE DI OUTPUT**
        right_panel = QVBoxLayout()

        # Etichetta superiore
        self.label = QLabel("Seleziona un'azione da eseguire!")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 14))
        right_panel.addWidget(self.label)

        # Area di output per il terminale
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Monospace", 10))
        right_panel.addWidget(self.terminal_output)

        # Campo di input per inviare comandi al processo
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Monospace", 10))
        self.input_field.setPlaceholderText("Digita un input e premi INVIO...")
        self.input_field.returnPressed.connect(self.send_input_to_process)
        right_panel.addWidget(self.input_field)

        main_layout.addLayout(right_panel, 2)  # 🔹 Il lato destro occupa il 70% (2/3)

        # Configura il layout principale
        self.setLayout(main_layout)

        # **Carichiamo i pulsanti delle action**
        self.create_action_buttons()

        # Processo per eseguire execute_action
        self.process = QProcess()
        self.process.setProcessChannelMode(
            QProcess.MergedChannels
        )  # 🔹 Unisce stdout e stderr
        self.process.readyReadStandardOutput.connect(self.update_terminal)
        self.process.readyReadStandardError.connect(self.update_terminal)

    def create_action_buttons(self):
        """
        Recupera le action disponibili e crea un pulsante per ognuna.
        """
        actions = get_action_registry()

        if not actions:
            self.terminal_output.append("⚠️ Nessuna azione disponibile!")
            return

        for action_name, action_data in actions.items():
            button = QPushButton(action_name)
            button.setFont(QFont("Arial", 12))
            button.clicked.connect(lambda _, a=action_name: self.run_action(a))
            self.action_layout.addWidget(button)

    def refresh_action_buttons(self):
        """
        Pulisce e ricarica la lista dei pulsanti delle action disponibili.
        """
        # Rimuove tutti i widget tranne il pulsante "Aggiorna Azioni"
        while (
            self.action_layout.count() > 1
        ):  # Mantiene solo il primo widget (refresh button)
            widget = self.action_layout.takeAt(1).widget()
            if widget:
                widget.deleteLater()

        self.create_action_buttons()  # Ricarica le action disponibili

    def run_action(self, action_name):
        """
        Avvia un'azione specifica usando `execute_action`.
        """
        self.label.setText(f"Esecuzione in corso: {action_name}")
        self.terminal_output.clear()
        self.input_field.clear()

        # Comando per eseguire l'azione
        command = "python"
        arguments = [
            "-c",
            f"from utils import execute_action; execute_action('{action_name}', None)",
        ]

        # Avvia il processo
        self.process.start(command, arguments)

    def update_terminal(self):
        """
        Aggiorna il terminale UI con l'output di `execute_action`.
        """
        output = self.process.readAllStandardOutput().data().decode()
        error_output = self.process.readAllStandardError().data().decode()

        if output:
            self.terminal_output.append(output)
        if error_output:
            self.terminal_output.append(f"⚠️ ERRORE: {error_output}")

        if self.process.state() == QProcess.NotRunning:
            self.label.setText("Seleziona un'azione da eseguire!")

    def send_input_to_process(self):
        """
        Invia l'input dell'utente al processo in esecuzione.
        """
        user_input = self.input_field.text()
        if self.process.state() == QProcess.Running:
            self.process.write(
                user_input.encode() + b"\n"
            )  # 🔹 Invia input con un newline
            self.process.waitForBytesWritten()
            self.input_field.clear()


# Avvio dell'applicazione
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActionLauncherApp()
    window.show()
    sys.exit(app.exec_())
