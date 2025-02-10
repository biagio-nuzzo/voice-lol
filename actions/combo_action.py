ACTION_CHAIN = {
    "metadata": {
        "name": "COMBO_ACTION",
        "description": "Acquisisce un input dall'utente via tastiera e lo restituisce.",
        "verbose_name": "Combo Action",
    },
    "steps": [
        {
            "function": "get_today",
            "input_key": None,
            "output_key": "today_date",
        },
        {
            "function": "generate_audio",
            "input_key": "today_date",
            "output_key": "output_audio",
        },
        {
            "function": "play_audio",
            "input_key": "output_audio",
            "output_key": "final_response",
        },
    ],
}
