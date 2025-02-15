# FastChain
from fastchain.core import Action


def auto_start_capture(next_action_name=None):
    """Avvia automaticamente la registrazione vocale specificando l'azione successiva.
    Ora richiama l'action START_CAPTURE per adattarsi alla nuova struttura."""
    print("[AUTO] Avvio automatico della registrazione (START_CAPTURE)...")
    from fastchain.manager import FastChainManager

    FastChainManager.run_action("START_CAPTURE", next_action_name)


AUTO_START_CAPTURE = Action(
    name="AUTO_START_CAPTURE",
    description="Avvia automaticamente la registrazione vocale e specifica un'azione successiva.",
    verbose_name="Avvio Automatico Registrazione",
    steps=[
        {
            "function": lambda next_action_name=None: auto_start_capture(
                next_action_name
            ),
            "input_type": str,
            "output_type": None,
        },
    ],
    input_action=True,
)
