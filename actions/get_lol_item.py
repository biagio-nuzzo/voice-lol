# Built-in
import json
import re

# Api
import requests

# Constants
from data.constants.items import LOL_ITEMS

# Settings
from settings import API_URL, GEMMA


# Funzione per interrogare l'LLM
def llm_get_item(user_input):
    pre_prompt = f"""
        Sei un sistema di identificazione per oggetti di League of Legends. Il tuo compito è **solo** restituire un JSON nel seguente formato:

        {{
            "item": "NOME_OGGETTO"
        }}

        Dove **NOME_OGGETTO** è uno dei seguenti valori esatti:
        - "LAMA_DI_DORAN"
        - "SIGILLO_OSCURO"
        - "CORAZZA_UOMO_MORTO"
        - "ARCO_SCUDO_IMMORTALE"
        - "MASCHERA_ABISSO"

        Se la richiesta dell'utente riguarda uno di questi oggetti, restituisci **solo il JSON corretto**. Se la richiesta non riguarda uno di questi oggetti, restituisci:

        {{
            "item": null
        }}

        ⚠️ **Regole importanti:**  
        1. **Non fornire spiegazioni.**  
        2. **Non generare più di un JSON.**  
        3. **Non aggiungere testo prima o dopo il JSON.**  

        **Input:** "{user_input}"
            """

    payload = {
        "model": GEMMA,
        "prompt": pre_prompt,
        "max_tokens": 5000,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()["choices"][0]["text"]
        match = re.search(r'\{\s*"item"\s*:\s*"(.*?)"\s*\}', data)
        if match:
            return {"item": match.group(1)}

    print(f"Errore nella richiesta: {response.status_code}")
    return {"item": None}


# Funzione per generare una descrizione dettagliata
def generate_description(item_key):
    item_info = LOL_ITEMS[item_key["item"]]
    description_prompt = f"""
        Genera una descrizione tra i 180 - 280 caratteri per il seguente oggetto di League of Legends:

        Nome: {item_key["item"].replace('_', ' ')}
        Descrizione: {item_info['description']}
        Statistiche: {json.dumps(item_info['statistics'], indent=4)}
        Effetti: {item_info['effects']}

        Restituisci solo la descrizione testuale.
        La descrizione deve essere solo testuale perché sarà convertita in audio.
        Quindi non includere informazioni visive o grafiche.
        Rispondi come se stessi parlando a voce all'utente.
        Non includere saluti.        
            """

    payload = {
        "model": GEMMA,
        "prompt": description_prompt,
        "max_tokens": 5000,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()

    return "Errore nella generazione della descrizione."


ACTION_CHAIN = {
    "metadata": {
        "description": "Restituisce una descrizione dettagliata di un oggetto di League of Legends.",
        "name": "GET_LOL_ITEMS",
        "verbose_name": "Descrivi Oggetto League of Legends",
    },
    "steps": [
        {
            "function": "llm_get_item",
            "input_key": "user_input",
            "output_key": "item_key",
        },
        {
            "function": "generate_description",
            "input_key": "item_key",
            "output_key": "final_response",
        },
    ],
}
