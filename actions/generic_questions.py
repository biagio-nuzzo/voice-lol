# Api
import requests
import re

# Settings
from settings import API_URL


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
        "model": "gemma-2-2b-instruct",
        "prompt": prompt,
        "max_tokens": 800,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()

    print(f"Errore nella richiesta: {response.status_code}")
    return None
