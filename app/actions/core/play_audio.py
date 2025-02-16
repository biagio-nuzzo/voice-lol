# FastChain
from fastchain.core import Action

# Utils
from app.utils import play_audio


class PlayAudioAction:
    """
    Classe che riproduce un file audio fornito in input.
    """

    def execute(self, audio_file: str) -> str:
        print(f"▶️ Riproduzione audio: {audio_file}")
        play_audio(audio_file)
        return "Audio riprodotto"


PLAY_AUDIO = Action(
    name="PLAY_AUDIO",
    description="Riproduce un file audio fornito in input.",
    verbose_name="Riproduzione Audio",
    core=True,
    steps=[
        {"function": PlayAudioAction().execute, "input_type": str, "output_type": str}
    ],
    input_action=False,
)
