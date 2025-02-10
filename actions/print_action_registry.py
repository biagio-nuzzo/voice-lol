# Import della funzione per recuperare il registro delle azioni
from utils import get_action_registry


def print_action_registry():
    """
    Recupera e stampa in console il registro delle azioni disponibili.
    """
    actions = get_action_registry()

    print("\n=== Action Registry Raw ===")
    print(actions)

    print("\n=== Action Registry ===")
    for name, data in actions.items():
        description = data["metadata"].get(
            "description", "Nessuna descrizione disponibile"
        )
        print(f"- {name}: {description}")

    print("======================\n")

    return {"status": "success", "message": "Registro delle azioni stampato in console"}


# Definizione della Action
ACTION_CHAIN = {
    "metadata": {
        "description": "Stampa in console il registro delle azioni disponibili.",
        "name": "PRINT_ACTION_REGISTRY",
        "verbose_name": "Stampa Registro Azioni",
        "input_action": False,
    },
    "steps": [
        {
            "function": "print_action_registry",
            "input_key": None,
            "output_key": "final_response",
        },
    ],
}
