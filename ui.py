import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont


class ActionLauncherApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configurazione finestra
        self.setWindowTitle("Action Launcher")
        self.setGeometry(300, 300, 500, 400)

        # Layout principale
        layout = QVBoxLayout()

        # Etichetta superiore
        self.label = QLabel("Premi il pulsante per avviare l'azione!")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 14))
        layout.addWidget(self.label)

        # Pulsante di esecuzione
        self.button = QPushButton("Esegui Azione")
        self.button.setFont(QFont("Arial", 12))
        self.button.clicked.connect(self.run_action)
        layout.addWidget(self.button)

        # Area di output per il terminale
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Monospace", 10))
        layout.addWidget(self.terminal_output)

        # Campo di input per inviare comandi al processo
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Monospace", 10))
        self.input_field.setPlaceholderText("Digita un input e premi INVIO...")
        self.input_field.returnPressed.connect(self.send_input_to_process)
        layout.addWidget(self.input_field)

        # Configura il layout principale
        self.setLayout(layout)

        # Processo per eseguire execute_action
        self.process = QProcess()
        self.process.setProcessChannelMode(
            QProcess.MergedChannels
        )  # 🔹 Unisce stdout e stderr
        self.process.readyReadStandardOutput.connect(self.update_terminal)
        self.process.readyReadStandardError.connect(self.update_terminal)

    def run_action(self):
        """
        Avvia `execute_action` in un processo separato senza bloccare la UI.
        """
        self.label.setText("Esecuzione in corso...")
        self.terminal_output.clear()
        self.input_field.clear()

        # Comando per eseguire execute_action nel processo separato
        command = "python"
        arguments = [
            "-c",
            "from utils import execute_action; execute_action('COMBO_TEXT_TO_AUDIO_PLAY', None)",
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
            self.label.setText("Azione completata!")

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
