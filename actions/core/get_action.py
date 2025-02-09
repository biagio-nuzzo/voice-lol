# Api
import requests
import re

# Settings
from settings import API_URL, GEMMA

from utils import get_action_registry


def generate_prompt(user_input):
    """
    Genera un prompt dinamico per classificare le richieste dell'utente basato sulle azioni registrate.
    """
    actions = get_action_registry()

    actions_list = "\n".join(
        [
            f'- "{name}": {data["metadata"]["description"]}'
            for name, data in actions.items()
        ]
    )

    prompt = f"""
        Sei un assistente AI che classifica le richieste degli utenti in base al contesto.
        Il tuo compito è identificare quale tra le seguenti azioni è richiesta dall'utente:

        {actions_list}

        ⚠️ **Regole importanti:**
        1. **Rispondi solo con un JSON nel formato:**
        ```json
        {{"action": "NOME_AZIONE"}}
        ```
        2. **Non fornire spiegazioni o testo extra.**
        3. **Se l'input dell'utente non è chiaro, scegli l'opzione più adatta.**

        **Input dell'utente:** "{user_input}"
        """

    return prompt


# Funzione per identificare l'azione richiesta dall'utente
def llm_get_action(user_input):
    prompt = generate_prompt(user_input)

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
            return {"action": match.group(1)}

    print(f"Errore nella richiesta: {response.status_code}")
    return {"action": None}


ACTION_CHAIN = {
    "metadata": {
        "description": "Identifica l'azione richiesta dall'utente.",
        "name": "GET_ACTION",
        "verbose_name": "Identificazione Azione",
    },
    "steps": [
        {
            "function": llm_get_action,
            "input_key": "user_input",
            "output_key": "final_response",
        },
    ],
}
