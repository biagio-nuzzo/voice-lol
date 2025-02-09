# Actions
from actions.get_lol_item import llm_get_item, generate_description
from actions.generic_question import llm_generic_question
from actions.get_action import llm_get_action
from actions.create_action import llm_create_action

# Definizione delle azioni supportate
ACTIONS = {
    "GET_ACTION": {
        "metadata": {
            "description": "Identifica l'azione richiesta dall'utente.",
        },
        "steps": [
            {
                "function": llm_get_action,
                "input_key": "user_input",
                "output_key": "final_response",
            },
        ],
    },
    "GET_LOL_ITEMS": {
        "metadata": {
            "description": "Restituisce una descrizione dettagliata di un oggetto di League of Legends.",
        },
        "steps": [
            {
                "function": llm_get_item,
                "input_key": "user_input",
                "output_key": "item_key",
            },
            {
                "function": generate_description,
                "input_key": "item_key",
                "output_key": "final_response",
            },
        ],
    },
    "GENERIC_QUESTION": {
        "metadata": {
            "description": "Risponde a una domanda generica.",
        },
        "steps": [
            {
                "function": llm_generic_question,
                "input_key": "user_input",
                "output_key": "final_response",
            },
        ],
    },
    "CREATE_ACTION": {
        "metadata": {
            "description": "Crea una nuova action su richiesta dell'utente.",
        },
        "steps": [
            {
                "function": llm_create_action,
                "input_key": "user_input",
                "output_key": "final_response",
            },
        ],
    },
}
