ACTION_CHAIN = {
    "metadata": {
        "name": "COMBO_ACTION",
        "description": "Acquisisce un input dall'utente via tastiera e lo restituisce.",
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_keyboard_input",
        },
        {
            "function": "llm_generic_question",
            "input_key": "user_keyboard_input",
            "output_key": "final_response",
        },
    ],
}
