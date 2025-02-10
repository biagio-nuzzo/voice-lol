def get_keyboard_input():
    """
    Acquisisce l'input da tastiera dell'utente e lo restituisce quando preme Invio.
    """
    user_input = input("⌨️ Digita il tuo comando e premi Invio: ")
    return user_input


# Definizione dell'action
ACTION_CHAIN = {
    "metadata": {
        "name": "GET_KEYBOARD_INPUT",
        "description": "Acquisisce un input dall'utente via tastiera e lo restituisce.",
        "verbose_name": "Input da Tastiera",
        "input_action": True,
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "final_response",
        }
    ],
}
