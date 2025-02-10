def print_value(value):
    """
    Stampa in console il valore dato in input.
    """
    print(f"🔹 Valore ricevuto: {value}")
    return value  # 🔹 Restituiamo il valore per compatibilità con altre action


# Definizione dell'action
ACTION_CHAIN = {
    "metadata": {
        "name": "PRINT_VALUE",
        "description": "Stampa in console un valore ricevuto in input.",
    },
    "steps": [
        {
            "function": "print_value",
            "input_key": "user_input",
            "output_key": "final_response",
        }
    ],
}
