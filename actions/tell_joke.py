import requests
from settings import API_URL, GEMMA

def generate_prompt(user_input):
    return f""" 
    Sei un assistente AI. Il tuo compito è: This function tells a joke about computers.
    Questo è l'input dell'utente: "{user_input}".
    """ 

def llm_action_name(user_input):
    payload = {
        "model": GEMMA,
        "prompt": generate_prompt(user_input),
        "max_tokens": 2000,
        "temperature": 0.7,
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    return "Error generating response."

ACTION_CHAIN = {
        "metadata": {
            "description": "This function tells a joke about computers.", 
            "name": "TELL_JOKE",
            "verbose_name": "TELL_JOKE",
            },
        "steps": [
            {
                "function": llm_action_name,
                "input_key": "user_input",
                "output_key": "final_response",
            }
        ],
}