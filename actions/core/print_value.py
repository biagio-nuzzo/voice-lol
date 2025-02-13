from FastChain.core import Action


def print_value(value):
    """
    Stampa in console il valore dato in input.
    """
    print(f"🔹 Valore ricevuto: {value}")
    return value  # 🔹 Restituiamo il valore per compatibilità con altre action


PRINT_VALUE_ACTION = Action(
    name="PRINT_VALUE",
    description="Stampa in console un valore ricevuto in input.",
    verbose_name="Stampa Valore",
    steps=[{"function": print_value, "input_type": str, "output_type": str}],
    input_action=False,
)
