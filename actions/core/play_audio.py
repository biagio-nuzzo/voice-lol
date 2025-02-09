# Utils
from utils import play_audio


def play_audio_wrapper(audio_file):
    """Riproduce il file audio generato."""
    print(f"▶️ Riproduzione audio: {audio_file}")
    play_audio(audio_file)

    return "Audio riprodotto"


ACTION_CHAIN = {
    "metadata": {
        "name": "PLAY_AUDIO",
        "description": "Riproduce un file audio fornito in input.",
    },
    "steps": [
        {
            "function": "play_audio_wrapper",
            "input_key": "user_input",
            "output_key": "final_response",
        }
    ],
}
