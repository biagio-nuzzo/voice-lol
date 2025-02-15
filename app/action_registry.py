# Actions Core
from actions.core.get_keyboard_input import GET_KEYBOARD_INPUT
from actions.core.print_value import PRINT_VALUE
from actions.core.capture_speech.capture_speech_actions import (
    START_CAPTURE,
    STOP_CAPTURE,
    WIDGET_TOGGLE_CAPTURE,
)

# Actions Custom
from actions.custom.print_value import PRINT_VALUE


# Dizionario che mappa tutte le Action disponibili
ACTION_REGISTRY = {
    # Core
    "GET_KEYBOARD_INPUT": GET_KEYBOARD_INPUT,
    "PRINT_VALUE": PRINT_VALUE,
    "START_CAPTURE": START_CAPTURE,
    "STOP_CAPTURE": STOP_CAPTURE,
    "WIDGET_TOGGLE_CAPTURE": WIDGET_TOGGLE_CAPTURE,
    # Custom
    "PRINT_VALUE": PRINT_VALUE,
}
