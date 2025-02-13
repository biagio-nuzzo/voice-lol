from FastChain.core import Action
from actions.core.capture_speech.capture_speech import CaptureSpeechAction
from actions.core.print_value import print_value

START_AGENT = Action(
    name="COMBO_GET_VOICE_PRINT",
    description="Acquisisce un input dall'utente via voce e lo stampa in console.",
    verbose_name="Input Vocale e Stampa",
    steps=[
        {
            "function": CaptureSpeechAction().execute,
            "input_type": None,
            "output_type": str,
        },
        {"function": print_value, "input_type": str, "output_type": str},
    ],
    input_action=True,
)
