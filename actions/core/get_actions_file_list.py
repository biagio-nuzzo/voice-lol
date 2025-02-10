import os


def list_files_in_actions(_=None):
    """Restituisce la lista di tutti i file Python presenti nelle cartelle actions/ e actions/core/."""
    base_actions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    core_actions_dir = os.path.join(base_actions_dir, "core")

    all_files = []

    def scan_directory(directory):
        """Scansiona una cartella e aggiunge i file Python alla lista."""
        if not os.path.exists(directory):
            print(f"⚠️ Attenzione: La cartella '{directory}' non esiste. Ignorata.")
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                all_files.append(filename)

    # Scansiona entrambe le cartelle
    scan_directory(base_actions_dir)
    scan_directory(core_actions_dir)

    print("📂 Actions trovate:", all_files)
    return all_files


# Definizione dell'action per elencare i file nella cartella "actions"
ACTION_CHAIN = {
    "metadata": {
        "name": "LIST_ACTIONS_FILE",
        "description": "Restituisce la lista dei file nella cartella actions",
        "verbose_name": "Elenco File Azioni",
        "input_action": False,
    },
    "steps": [
        {
            "function": "list_files_in_actions",
            "input_key": None,
            "output_key": "final_response",
        }
    ],
}
