import requests
from utils import get_action_registry
from settings import API_URL, GEMMA


def generate_prompt():
    """
    Genera un prompt per l'LLM che descrive tutte le azioni disponibili.
    """
    actions = get_action_registry()

    actions_list = "\n".join(
        [
            f'- {data["metadata"]["verbose_name"]}: {data["metadata"]["description"]}'
            for data in actions.values()
        ]
    )

    return f"""
        Basati sulle azioni che trovi di seguito per generare un testo naturale che verrà
        convertito in audio da far ascoltare all'utente. Il testo deve essere usato per dare 
        all'utente la lista delle azioni disponibili, con una breve descrizione annessa.
        
        {actions_list}
        
        ⚠️ **Regole importanti:**
        1. **Rispondi con un testo naturale che descrive le azioni disponibili.**
        5. **Non includere codice o comandi.**
        6. **Non includere i tuoi pensieri**

    """


def llm_list_actions(user_input):
    """
    Chiama l'LLM per generare un testo leggibile contenente la lista delle azioni disponibili.
    """
    prompt = generate_prompt()

    print("PROMPT LIST ACTIONS", prompt)

    payload = {
        "model": GEMMA,
        "prompt": prompt,
        "max_tokens": -1,
        "temperature": 0.3,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        print("RESPONSE MODELLO", response.json())
        return response.json()["choices"][0]["text"].strip()

    return "Errore nella generazione della risposta."


ACTION_CHAIN = {
    "metadata": {
        "description": "Genera una descrizione vocale delle azioni disponibili dell'assistente.",
        "name": "LIST_AVAILABLE_ACTIONS",
        "verbose_name": "Elenco Azioni Disponibili",
    },
    "steps": [
        {
            "function": llm_list_actions,
            "input_key": "user_input",
            "output_key": "final_response",
        }
    ],
}
