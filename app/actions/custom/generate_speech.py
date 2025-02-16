# FastChain
from fastchain.core import Action

# Actions
from app.actions.core.get_keyboard_input import GET_KEYBOARD_INPUT
from app.actions.core.text_to_audio.text_to_audio import TEXT_TO_AUDIO
from app.actions.core.play_audio import PLAY_AUDIO

GENERATE_SPEECH = Action(
    name="GENERATE_SPEECH",
    description="Genera un file audio a partire da un testo dato.",
    verbose_name="Genera Audio da Testo",
    steps=GET_KEYBOARD_INPUT.get_steps()
    + TEXT_TO_AUDIO.get_steps()
    + PLAY_AUDIO.get_steps(),
    input_action=False,
)
