from fastchain.core import Action


class RunActionAction:
    """
    Classe che esegue l'azione il cui nome viene fornito in input.
    L'input atteso è il nome di un'azione (output di GET_ACTION).
    """

    def execute(self, action_name: str) -> str:
        from fastchain.manager import FastChainManager

        result = FastChainManager.run_action(action_name)
        return result


RUN_ACTION = Action(
    name="RUN_ACTION",
    description="Esegue l'azione richiesta dall'utente, dove l'input è l'output di GET_ACTION.",
    verbose_name="Esecuzione Azione",
    core=True,
    steps=[
        {"function": RunActionAction().execute, "input_type": str, "output_type": str}
    ],
)
