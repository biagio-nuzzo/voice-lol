# FastChain
from fastchain.core import Action
from dotenv import load_dotenv
import os
import imaplib
import email


class GetUnreadEmailsAction:
    def execute(self, _=None):
        """
        Ottiene le email non lette dalla inbox di Gmail utilizzando le credenziali dal file .env.

        Le credenziali vengono lette da:
          - EMAIL_SENDER: l'indirizzo email (mittente)
          - EMAIL_PASSWORD: la password per l'app

        Ritorna una lista di dizionari, ciascuno contenente:
          - "From": indirizzo del mittente
          - "Subject": oggetto dell'email
          - "Body": corpo dell'email (testo)

        NOTA: Le email vengono prelevate senza essere contrassegnate come lette.
        """
        load_dotenv()
        username = os.getenv("EMAIL_SENDER")
        app_password = os.getenv("EMAIL_PASSWORD")

        if not username or not app_password:
            return "Errore: EMAIL_SENDER o EMAIL_PASSWORD non sono impostati nel file .env."

        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(username, app_password)
            mail.select("inbox")

            # Usa BODY.PEEK[] per non segnare le email come lette
            status, response = mail.search(None, "(UNSEEN)")
            email_ids = response[0].split()
            results = []

            for e_id in email_ids:
                status, msg_data = mail.fetch(e_id, "(BODY.PEEK[])")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Estrai il corpo dell'email
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(
                                    part.get("Content-Disposition")
                                )
                                if (
                                    content_type == "text/plain"
                                    and "attachment" not in content_disposition
                                ):
                                    charset = part.get_content_charset() or "utf-8"
                                    body = part.get_payload(decode=True).decode(
                                        charset, errors="replace"
                                    )
                                    break
                        else:
                            charset = msg.get_content_charset() or "utf-8"
                            body = msg.get_payload(decode=True).decode(
                                charset, errors="replace"
                            )

                        results.append(
                            {
                                "From": msg.get("From"),
                                "Subject": msg.get("Subject"),
                                "Body": body,
                            }
                        )
            mail.logout()
            return results
        except Exception as e:
            return f"Errore durante l'accesso alle email: {e}"


GET_UNREAD_EMAILS = Action(
    name="GET_UNREAD_EMAILS",
    description="Ottiene le email non lette dalla inbox di Gmail e le restituisce in una lista di dizionari, includendo mittente, oggetto e corpo. Le email rimangono non lette.",
    verbose_name="Email Non Lettere",
    core=True,
    steps=[
        {
            "function": GetUnreadEmailsAction().execute,
            "input_type": None,
            "output_type": list,
        }
    ],
    input_action=False,
)
