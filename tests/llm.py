import requests

# Imposta l'URL dell'API di LM Studio
API_URL = "http://localhost:1234/v1/completions"


pre_prompt = """
Sei un sistema di identificazione per oggetti di League of Legends. Il tuo compito è **solo** restituire un JSON nel seguente formato:

{
    "item": "NOME_OGGETTO"
}

Dove **NOME_OGGETTO** è uno dei seguenti valori esatti:
- "LAMA_DI_DORAN"
- "SIGILLO_OSCURO"
- "CORAZZA_DELL_UOMO_MORTO"
- "ARCO_SCUDO_IMMORTALE"
- "MASCHERA_DELL_ABISSO"

Se la richiesta dell'utente riguarda uno di questi oggetti, restituisci **solo il JSON corretto**.
Se la richiesta non riguarda uno di questi oggetti, restituisci quella più simile.

⚠️ **Regole importanti:**  
1. **Non fornire spiegazioni.**  
2. **Non generare più di un JSON.**  
3. **Non aggiungere testo prima o dopo il JSON.**  
4. **Non modificare il formato del JSON.**
5. **FORNISCI SOLO UNA RISPOSTA**
6. **FORNISCI SEMPRE UNA RISPOSTA**

**Input:** "{testo}"
"""


# Corpo della richiesta
payload = {
    "model": "gemma-2-2b-instruct",  # Sostituisci con il nome del tuo modello caricato su LM Studio
    "prompt": pre_prompt,
    "max_tokens": 200,
    "temperature": 0.7,
}

# Invia la richiesta POST
response = requests.post(API_URL, json=payload)

# Controlla la risposta
if response.status_code == 200:
    data = response.json()
    print("Risposta del modello:")
    print(data["choices"][0]["text"])
else:
    print(f"Errore nella richiesta: {response.status_code}")
    print(response.text)
