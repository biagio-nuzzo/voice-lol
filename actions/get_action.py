# Api
import requests
import re

# Settings
from settings import API_URL

# Definizione delle azioni disponibili
AVAILABLE_ACTIONS = ["GET_LOL_ITEMS", "GENERIC_QUESTION"]


# Funzione per identificare l'azione richiesta dall'utente
def llm_get_action(user_input):
    prompt = f"""
        Sei un assistente AI che classifica le richieste degli utenti in base al contesto.
        Il tuo compito è identificare quale tra le seguenti azioni è richiesta dall'utente:

        - "GET_LOL_ITEMS" → Se l'utente chiede informazioni su un oggetto di League of Legends.
        - "GENERIC_QUESTION" → Se l'utente fa una domanda generica non correlata agli oggetti di LoL.

        ⚠️ **Regole importanti:**
        1. **Rispondi solo con un JSON nel formato:**
        ```json
        {{"action": "NOME_AZIONE"}}
        ```
        2. **Non fornire spiegazioni o testo extra.**
        3. **Se l'input dell'utente non è chiaro, scegli l'opzione più adatta.**

        **Input dell'utente:** "{user_input}"
        """

    payload = {
        "model": "gemma-2-2b-instruct",
        "prompt": prompt,
        "max_tokens": 100,
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
