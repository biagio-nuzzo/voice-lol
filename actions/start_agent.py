ACTION_CHAIN = {
    "metadata": {
        "name": "START_AGENT",
        "description": "Action di test per testare la concatenazione di azioni",
        "verbose_name": "Combo Action",
        "input_action": False,
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_keyboard_input",
        },
    ],
}
