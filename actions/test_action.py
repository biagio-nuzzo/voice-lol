ACTION_CHAIN = {
    "metadata": {
        "name": "TEST_ACTION",
        "description": "Action di test per testare la concatenazione di azioni",
        "verbose_name": "Combo Action",
    },
    "steps": [
        {
            "function": "get_keyboard_input",
            "input_key": None,
            "output_key": "user_keyboard_input",
        },
        {
            "function": "llm_action_name",
            "input_key": "user_keyboard_input",
            "output_key": "llm_response",
        },
        {
            "function": "generate_audio",
            "input_key": "llm_response",
            "output_key": "audio_file",
        },
        {
            "function": "play_audio",
            "input_key": "audio_file",
            "output_key": "final_response",
        },
    ],
}
