# Built-in
import os
import re
import json
import time

# APIs
import requests

# Settings
from settings import API_URL, QWEN, GEMMA


actions_dir = os.path.join(os.path.dirname(__file__))


def llm_generate_action_code(action_name, action_description):
    """
    Genera il codice di una nuova action basata sulla richiesta dell'utente.
    """
    prompt = f"""
    Crea l'azione "{action_name}" con la seguente descrizione: "{action_description}".
    
    La risposta deve essere esclusivamente il codice python per la nuova action, senza alcun testo aggiuntivo.

    Di seguito trovi un esempio di come dovrebbe apparire il codice:

    import requests
    from settings import API_URL, GEMMA

    def generate_prompt(user_input):
        return f\"\"\" 
        Sei un assistente AI. Il tuo compito è: ACTION_DESCRIPTION.
        Questo è l'input dell'utente: "USER_INPUT".
        \"\"\" 

    def llm_action_name(user_input):
        payload = {{
            "model": GEMMA,
            "prompt": generate_prompt(user_input),
            "max_tokens": 2000,
            "temperature": 0.7,
        }}
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"].strip()
        return "Error generating response."

    ACTION_CHAIN = {{
            "metadata": {{
                "description": "ACTION_DESCRIPTION", 
                "name": "ACTION_NAME",
                "verbose_name": "ACTION_NAME",
                }},
            "steps": [
                {{
                    "function": "llm_action_name",
                    "input_key": "user_input",
                    "output_key": "final_response",
                }}
            ],
    }}

    L'azione richiesta dall'utente potrebbe avere più step o richiedere una logica più complessa.
    Restituiscimi SOLO il codice Python per la nuova action, senza alcun testo aggiuntivo.
    I prompt devono essere sempre scritti in italiano.
    I nomi delle action devono sempre essere in inglese.
    """

    payload = {
        "model": QWEN,
        "prompt": prompt,
        "max_tokens": 5000,
        "temperature": 0.5,
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        print("✅ Action generata con successo!")
        code = response.json()["choices"][0]["text"]
        code = code.split("```python")[1].split("```")[0].strip()
        print("CODE", code)
        return code
    return None


def write_action_file(action_name, action_code):
    """
    Scrive il codice della nuova action in un file Python nella cartella actions.
    """
    action_path = os.path.join(actions_dir, f"{action_name.lower()}.py")
    with open(action_path, "w", encoding="utf-8") as f:
        f.write(action_code)
    print(f"✅ Action creata: {action_path}")


def llm_create_action(user_input):
    """
    Estrae il nome e la descrizione della nuova action dall'input utente e la genera.
    """

    extraction_prompt = f"""
    Your task is to extract the name and description of the action requested by the user.
    You must **only** return a JSON in the following format, without any extra text, explanations, or additional formatting:

    ```json
    {{
        "name": "ACTION_NAME",
        "description": "This function allows you to generate jokes by querying an LLM model."
    }}
    ```

    example:
    ```json
    {{
        "name": "GET_HISTORY_FACTS",
        "description": "This function retrieves historical facts from a given date."
    }}
    ```
    ⚠️ Important Rules:

    Do not add any explanations or introductory text.
    Do not generate the action itself—just extract the name and description.
    Only return a valid JSON response.
    Do not include Markdown formatting or any additional text outside the JSON.
    Do not include any code snippets or additional information.
    Do not generate any code or additional output.

    User Input: "{user_input}"
    """

    payload = {
        "model": GEMMA,
        "prompt": extraction_prompt,
        "max_tokens": 5000,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        data = response.json()["choices"][0]["text"].strip()

        print("Data", data)

        # Estrai solo la parte JSON
        match = re.search(r"\{.*\}", data, re.DOTALL)

        if match:
            json_text = match.group(0)  # Otteniamo il JSON come stringa
            try:
                action_data = json.loads(json_text)  # Convertiamo in un dict
                action_name = action_data.get("name")
                action_description = action_data.get("description")

                if action_name and action_description:
                    attempts = 0
                    max_attempts = 3
                    action_code = None

                    while attempts < max_attempts:
                        try:
                            action_code = llm_generate_action_code(
                                action_name, action_description
                            )
                            if action_code:
                                break  # Uscire dal ciclo se la generazione è riuscita
                        except Exception as e:
                            print(
                                f"Errore nella generazione dell'action (tentativo {attempts + 1}): {e}"
                            )
                            attempts += 1
                            time.sleep(2)  # Ritardo tra i tentativi

                    if action_code:
                        write_action_file(action_name, action_code)
                        print(f"Action {action_name} creata con successo!")
                        return f"Action {action_name} creata con successo!"
                    else:
                        print("Errore: impossibile generare l'action dopo 3 tentativi.")
            except json.JSONDecodeError:
                print("Errore nel parsing del JSON.")
        else:
            print("Nessun JSON valido trovato nella risposta.")
    return "Errore nella creazione della action."


ACTION_CHAIN = {
    "metadata": {
        "description": "Crea una nuova action su richiesta dell'utente.",
        "name": "CREATE_ACTION",
        "verbose_name": "Creazione Azione",
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_input",
        },
        {
            "function": "llm_create_action",
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
