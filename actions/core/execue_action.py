# Import necessari
from utils import get_action_registry


def execute_action(action_name):
    """
    Identifica e esegue l'azione richiesta dall'utente.

    :param user_input: Stringa contenente il comando dell'utente.
    :param kwargs: Eventuali parametri aggiuntivi per l'azione.
    :return: Il risultato dell'azione eseguita.
    """
    if not action_name:
        return {"error": "Nessuna azione identificata"}

    actions = get_action_registry()

    if action_name not in actions:
        return {"error": f"Azione '{action_name}' non trovata nel registro"}

    action_function = actions[action_name]["function"]

    try:
        result = action_function()
        return {"action": action_name, "result": result}
    except Exception as e:
        return {
            "error": f"Errore durante l'esecuzione dell'azione '{action_name}': {str(e)}"
        }


ACTION_EXECUTION = {
    "metadata": {
        "description": "Identifica ed esegue l'azione richiesta dall'utente.",
        "name": "EXECUTE_ACTION",
        "verbose_name": "Esecuzione Azione",
        "input_action": False,
    },
    "steps": [
        {
            "function": "execute_action",
            "input_key": "action_name",
            "output_key": "final_response",
        },
    ],
}
