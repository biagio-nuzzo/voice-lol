# FastChain
from fastchain.core import Action

# Actions
from app.actions.core.send_email import SEND_EMAIL
from app.actions.core.get_keyboard_input import GET_KEYBOARD_INPUT


class SendInput:
    def execute(self):
        """
        Ritorna il dizionario di configurazione per il dialogo che raccoglie i dati necessari:
          - destinatario: indirizzo email del destinatario (campo piccolo)
          - corpo: contenuto della mail (campo grande)
        """
        return {
            "title": "Invia Email",
            "inputs": [
                {
                    "name": "receiver",
                    "title": "Destinatario",
                    "description": "Inserisci l'indirizzo email del destinatario",
                    "size": "small",
                },
                {
                    "name": "body",
                    "title": "Corpo della Email",
                    "description": "Inserisci il contenuto della email",
                    "size": "large",
                },
            ],
        }


SEND_EMAIL_MANUAL = Action(
    name="SEND_EMAIL_MANUAL",
    description="""Invia un'email utilizzando il server SMTP di Gmail.
    L'utente può richiedere l'avvio di questa action dicendo "Invia email" e seguendo le istruzioni,
    oppure direttamente "Invia email a [email] con oggetto [oggetto] e corpo [corpo]".
    """,
    verbose_name="Invio Email Manuale",
    steps=[
        {
            "function": SendInput().execute,
            "input_type": None,
            "output_type": dict,
        }
    ]
    + GET_KEYBOARD_INPUT.get_steps()
    + SEND_EMAIL.get_steps(),
    input_action=False,
)
