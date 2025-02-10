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
        "input_action": False,
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_input",
        },
        {
            "function": "llm_get_item",
            "input_key": "user_input",
            "output_key": "lol_item",
        },
        {
            "function": "generate_description",
            "input_key": "lol_item",
            "output_key": "lol_item_description",
        },
        {
            "function": "print_value",
            "input_key": "lol_item_description",
            "output_key": "final_response",
        },
    ],
}


# Come vedi ci sono delle azioni che hanno come valore "input_action = True" queste azioni sono quelle che servono per acquisire l'input dell'utente. Ci sono invece azioni che hanno necessariamente bisogno di un input, come ad esempio la action "generic question". Voglio che quando parlo con il mio agent gli possa chiedere cose come "potresti darmi indicazioni sulla spada di doran?" Qui partirà la action "GET_ACTION" che mi identificherà che l'utente ha richiesto di ottenere informazioni su oggetti di lol, quindi sta invocando la funzione GET_LOL_ITEMS.
# La action GET_LOL_ITEMS, ha come primo step quello di acquisire l'input dell'utente, quindi se lancio direttamente la funzione GET_LOL_ITEMS questa mi chiederà prima l'input e poi passerà agli step successivi. Ma nel caso in cui io sto parlando con il mio agent, e lui ha identificato automaticamente la funzione, l'input ce l'ho già. Dunque vorrei modificare la funzione execute_action affinché:
