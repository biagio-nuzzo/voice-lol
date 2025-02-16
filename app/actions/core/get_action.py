import requests
import re

# Settings
from app.settings import API_URL, GEMMA

# Import della nuova Action dal framework
from fastchain.core import Action


class GetAction:
    """
    Classe per identificare l'azione richiesta dall'utente invocando il modello LLM.
    """

    def generate_prompt(self, user_input: str) -> str:
        """
        Genera un prompt dinamico per classificare le richieste degli utenti basato sulle azioni registrate.
        """
        from fastchain.manager import FastChainManager

        actions = FastChainManager.get_available_actions()
        actions_list = "\n".join(
            [
                f'- "{action["name"]}": {action["verbose_name"]} - {action["description"]}'
                for action in actions
            ]
        )
        prompt = f"""
            Sei un assistente AI che classifica le richieste degli utenti in base al contesto.
            Il tuo compito è identificare quale tra le seguenti azioni è richiesta dall'utente:

            {actions_list}

            Regole importanti:
            1. Rispondi solo con un JSON nel formato: {{"action": "NOME_AZIONE"}}
            2. Non fornire spiegazioni o testo extra.
            3. Se l'input dell'utente non è chiaro, scegli l'opzione più adatta.

            Input dell'utente: "{user_input}"
        """
        return prompt

    def execute(self, user_input: str) -> str:
        """
        Identifica l'azione richiesta dall'utente invocando il modello LLM.
        """
        prompt = self.generate_prompt(user_input)
        payload = {
            "model": GEMMA,
            "prompt": prompt,
            "max_tokens": 5000,
            "temperature": 0.7,
        }

        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()["choices"][0]["text"]
            match = re.search(r'\{\s*"action"\s*:\s*"(.*?)"\s*\}', data)
            if match:
                return match.group(1)

        print(f"Errore nella richiesta: {response.status_code}")
        return ""


GET_ACTION = Action(
    name="GET_ACTION",
    description="Identifica l'azione richiesta dall'utente.",
    verbose_name="Identificazione Azione",
    core=True,
    steps=[
        {
            "function": GetAction().execute,
            "input_type": str,
            "output_type": str,
            "thread": True,
        }
    ],
)
