# Actions Core
from app.actions.core.get_keyboard_input import GET_KEYBOARD_INPUT
from app.actions.core.capture_speech.capture_speech_actions import (
    START_CAPTURE,
    STOP_CAPTURE,
    WIDGET_TOGGLE_CAPTURE,
)
from app.actions.core.get_action import GET_ACTION
from app.actions.core.run_action import RUN_ACTION
from app.actions.core.text_to_audio.text_to_audio import TEXT_TO_AUDIO
from app.actions.core.play_audio import PLAY_AUDIO
from app.actions.core.start_agent import START_AGENT
from app.actions.core.send_email import SEND_EMAIL

# Actions Custom
from app.actions.custom.print_value import PRINT_VALUE
from app.actions.custom.generate_speech import GENERATE_SPEECH
from app.actions.custom.send_email_manual import SEND_EMAIL_MANUAL


# Dizionario che mappa tutte le Action disponibili
ACTION_REGISTRY = {
    # Core
    "GET_KEYBOARD_INPUT": GET_KEYBOARD_INPUT,
    "PRINT_VALUE": PRINT_VALUE,
    "START_CAPTURE": START_CAPTURE,
    "STOP_CAPTURE": STOP_CAPTURE,
    "WIDGET_TOGGLE_CAPTURE": WIDGET_TOGGLE_CAPTURE,
    "GET_ACTION": GET_ACTION,
    "RUN_ACTION": RUN_ACTION,
    "TEXT_TO_AUDIO": TEXT_TO_AUDIO,
    "PLAY_AUDIO": PLAY_AUDIO,
    "SEND_EMAIL": SEND_EMAIL,
    # Custom
    "PRINT_VALUE": PRINT_VALUE,
    "START_AGENT": START_AGENT,
    "GENERATE_SPEECH": GENERATE_SPEECH,
    "SEND_EMAIL_MANUAL": SEND_EMAIL_MANUAL,
}
