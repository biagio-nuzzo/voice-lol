from fastchain.core import Action

from app.actions.core.get_keyboard_input import GET_KEYBOARD_INPUT


def print_value(value):
    """
    Stampa in console il valore dato in input.
    """
    try:
        from fastchain.manager import FastChainManager

        actions = FastChainManager.get_available_actions()
        print(f"🔹 Action disponibili: {actions}")
    except Exception as e:
        print(f"[ERROR] Durante il recupero delle azioni: {e}")
    print(f"🔹 Valore ricevuto: {value}")
    return value  # 🔹 Restituiamo il valore per compatibilità con altre action


PRINT_VALUE = Action(
    name="PRINT_VALUE",
    description="Stampa in console un valore ricevuto in input.",
    verbose_name="Stampa Valore",
    steps=GET_KEYBOARD_INPUT.get_steps()
    + [{"function": print_value, "input_type": str, "output_type": str}],
    input_action=False,
)
