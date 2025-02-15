# Actions Core
from actions.core.get_keyboard_input import GET_KEYBOARD_INPUT_ACTION
from actions.core.print_value import PRINT_VALUE_ACTION
from actions.core.capture_speech.capture_speech import (
    START_CAPTURE,
    STOP_CAPTURE,
    WIDGET_TOGGLE_CAPTURE,
)

# Actions Custom
from actions.custom.auto_start_capture import AUTO_START_CAPTURE

# Dizionario che mappa tutte le Action disponibili
ACTION_REGISTRY = {
    "GET_KEYBOARD_INPUT": GET_KEYBOARD_INPUT_ACTION,
    "PRINT_VALUE": PRINT_VALUE_ACTION,
    "AUTO_START_CAPTURE": AUTO_START_CAPTURE,
    "START_CAPTURE": START_CAPTURE,
    "STOP_CAPTURE": STOP_CAPTURE,
    "WIDGET_TOGGLE_CAPTURE": WIDGET_TOGGLE_CAPTURE,
}
