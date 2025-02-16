# Built-in
import os

# FastChain
from fastchain.core import Action

# Email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Env
from dotenv import load_dotenv


class SendEmailAction:
    def execute(self, params):
        """
        Invia un'email utilizzando il server SMTP di Gmail.

        Parametri attesi nel dizionario 'params':
          - receiver: indirizzo email del receiver.
          - body: contenuto testuale della mail.

        Le credenziali vengono caricate dal file .env.
        """
        # Carica le variabili d'ambiente
        load_dotenv()
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")

        # Estrae i parametri passati
        receiver = params.get("receiver")
        body = params.get("body")

        # Validazione dei parametri
        if not receiver:
            return "Errore: receiver non specificato."
        if not body:
            return "Errore: body della mail non specificato."

        # Creazione del messaggio email
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "Oggetto della mail"
        msg.attach(MIMEText(body, "plain"))

        try:
            # Connessione al server SMTP di Gmail tramite SSL (porta 465)
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            return "Email inviata con successo!"
        except Exception as e:
            return f"Errore durante l'invio dell'email: {e}"


SEND_EMAIL = Action(
    name="SEND_EMAIL",
    description="Invia un'email utilizzando il server SMTP di Gmail. Parametri attesi: receiver, body della mail.",
    verbose_name="Invio Email",
    core=True,
    steps=[
        {
            "function": SendEmailAction().execute,
            "input_type": dict,
            "output_type": str,
        },
    ],
    input_action=True,
)
