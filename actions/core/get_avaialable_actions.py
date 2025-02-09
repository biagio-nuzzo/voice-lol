from utils import get_action_registry


def generate_action_list_text():
    """
    Genera un testo statico contenente l'elenco delle azioni disponibili.
    """
    actions = get_action_registry()

    actions_list = "\n".join(
        [
            f"{action_name}: {action['metadata']['description']}"
            for action_name, action in actions.items()
        ]
    )

    return f"""
        L'assistente è in grado di eseguire le seguenti azioni:
        {actions_list}
    """


def list_available_actions():
    """
    Restituisce il testo statico contenente la lista delle azioni disponibili.
    """
    return generate_action_list_text()


ACTION_CHAIN = {
    "metadata": {
        "description": "Genera una descrizione vocale delle azioni disponibili dell'assistente.",
        "name": "LIST_AVAILABLE_ACTIONS",
        "verbose_name": "Elenco Azioni Disponibili",
    },
    "steps": [
        {
            "function": list_available_actions,
            "input_key": None,
            "output_key": "final_response",
        }
    ],
}
