ACTION_CHAIN = {
    "metadata": {
        "name": "COMBO_TEXT_TO_AUDIO_PLAY",
        "description": "Acquisisce input dalla tastiera, lo converte in audio e lo riproduce.",
    },
    "steps": [
        {
            "function": "capture_speech_action",  # Step 1: Prende input dalla tastiera
            "input_key": None,
            "output_key": "speech_text",
        },
        {
            "function": "generate_audio",  # Step 2: Converte il testo in audio
            "input_key": "speech_text",
            "output_key": "audio_file",
        },
        {
            "function": "play_audio_wrapper",  # Step 3: Riproduce l'audio generato
            "input_key": "audio_file",
            "output_key": "final_response",
        },
    ],
}
