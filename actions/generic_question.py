# Api
import requests

# Settings
from settings import API_URL, GEMMA


# Funzione per interrogare l'LLM su una domanda generica
def llm_generic_question(user_input):
    prompt = f"""
Sei un assistente AI avanzato. Il tuo compito è rispondere in modo chiaro e informativo alle domande degli utenti.
La risposta che fornirai dovrà avere una lunghezza di minimo 250 caratteri e massimo 350 caratteri (salvo che l'utente non chieda diversamente).
Il tuo obiettivo è creare un testo che venga riprodotto da un sintetizzatore vocale, quindi non includere informazioni visive o grafiche.
Non generare più di una risposta.
La tua risposta verrà convertita in testo così come la fornirai, quindi assicurati di scrivere solo il necessario.

**Domanda:** "{user_input}"
"""

    payload = {
        "model": GEMMA,
        "prompt": prompt,
        "max_tokens": 5000,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()

    print(f"Errore nella richiesta: {response.status_code}")
    return None


ACTION_CHAIN = {
    "metadata": {
        "description": "Risponde a una domanda generica.",
        "name": "GENERIC_QUESTION",
        "verbose_name": "Risposta Domanda Generica",
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_input",
        },
        {
            "function": "llm_generic_question",
            "input_key": "user_input",
            "output_key": "output_text",
        },
        {
            "function": "print_value",
            "input_key": "output_text",
            "output_key": None,
        },
    ],
}
