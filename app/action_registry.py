from actions.core.get_keyboard_input import GET_KEYBOARD_INPUT_ACTION
from actions.core.print_value import PRINT_VALUE_ACTION
from actions.custom.start_agent import START_AGENT
from actions.core.capture_speech.capture_speech import CAPTURE_SPEECH_ACTION

# Dizionario che mappa tutte le Action disponibili
ACTION_REGISTRY = {
    "GET_KEYBOARD_INPUT": GET_KEYBOARD_INPUT_ACTION,
    "PRINT_VALUE": PRINT_VALUE_ACTION,
    "START_AGENT": START_AGENT,
    "CAPTURE_SPEECH": CAPTURE_SPEECH_ACTION,
}
