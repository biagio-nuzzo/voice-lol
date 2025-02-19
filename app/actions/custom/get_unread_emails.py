# FastChain
from fastchain.core import Action

# Actions
from app.actions.core.get_emails import GET_UNREAD_EMAILS
from app.actions.core.show_output import SHOW_OUTPUT

# Librerie
import textwrap


class EmailsToTextAction:
    def execute(self, params=None):
        """
        Trasforma una lista di email non lette in un testo formattato per la visualizzazione.

        Il parametro 'params' deve essere una lista di dizionari, dove ogni dizionario rappresenta
        un'email e contiene le seguenti chiavi:
          - 'From': mittente, ad esempio "Biagio Nuzzo <biagio.nuzzo.eco@gmail.com>"
          - 'Subject': oggetto dell'email
          - 'Body': corpo dell'email

        Per ciascuna email, il testo sarà formattato come segue:

        ========================================
        Da: [From]
        Oggetto: [Subject]
        Corpo:
        [Body]
        ========================================

        Se non sono presenti email, viene restituito un messaggio che indica l'assenza di email non lette.

        Inoltre, la dimensione del dialog (small, medium, large) viene scelta in base al numero di email:
          - ≤ 3 email  → small
          - 4-6 email  → medium
          - > 6 email  → large

        Ritorna un dizionario nel formato atteso da SHOW_OUTPUT:
        {
            'text': <testo formattato>,
            'config': {'title': 'Email non lette', 'size': <small|medium|large>}
        }
        """
        emails = params or []
        if not emails:
            formatted_text = "Nessuna email non letta."
        else:
            formatted_text = ""
            # Separatore più evidente, con un po' di spaziatura
            separator = "\n" + "=" * 40 + "\n\n"
            for email in emails:
                from_ = email.get("From", "Sconosciuto")
                subject = email.get("Subject", "Nessun Oggetto")
                body = email.get("Body", "")
                # Forza l'andata a capo per testi troppo lunghi
                subject_wrapped = textwrap.fill(subject, width=70)
                body_wrapped = textwrap.fill(body, width=70)
                formatted_text += separator
                formatted_text += f"Da: {from_}\n"
                formatted_text += f"Oggetto: {subject_wrapped}\n"
                formatted_text += "Corpo:\n"
                formatted_text += f"{body_wrapped}\n"
                formatted_text += separator + "\n"

        # Determina la dimensione in base al numero di email
        email_count = len(emails)
        if email_count <= 3:
            size = "small"
        elif email_count <= 6:
            size = "medium"
        else:
            size = "large"

        return {
            "text": formatted_text,
            "config": {"title": "Email non lette", "size": size},
        }


EMAIL_NON_LETTE = Action(
    name="EMAIL_NON_LETTE",
    description="""
    Ottiene le email non lette dalla inbox di Gmail e le restituisce in una lista di dizionari, 
    includendo mittente, oggetto e corpo. Le email rimangono non lette.
    L'utente può richiedere di attivare questa funzione dicendo:
    "Mostrami le email non lette" oppure "Mostrami le email non lette da Gmail".
    "Verifica se ci sono email da leggere",
    "Controlla se ci sono email non lette".
    """,
    verbose_name="Email Non Lettere",
    steps=GET_UNREAD_EMAILS.get_steps()
    + [
        {
            "function": EmailsToTextAction().execute,
            "input_type": list,
            "output_type": dict,
        }
    ]
    + SHOW_OUTPUT.get_steps(),
    input_action=False,
)
