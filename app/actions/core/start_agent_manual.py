from fastchain.core import Action
from app.actions.core.get_action import GET_ACTION
from app.actions.core.run_action import RUN_ACTION
from app.actions.core.get_keyboard_input import GET_KEYBOARD_INPUT


class SendInput:
    def execute(self):
        """
        Invia l'input testuale.
        """

        return {
            "title": "Come ti posso aiutare?",
            "inputs": [
                {
                    "name": "command",
                    "title": "Comando",
                    "description": "Inserisci il comando da eseguire",
                    "size": "medium",
                }
            ],
        }


START_AGENT_MANUAL = Action(
    name="START_AGENT",
    description="Concatena GET_ACTION e RUN_ACTION: acquisisce il nome dell'azione e la esegue.",
    verbose_name="Avvio Agente",
    core=True,
    steps=[
        {
            "function": SendInput().execute,
            "input_type": None,
            "output_type": dict,
            "thread": True,
        }
    ]
    + GET_KEYBOARD_INPUT.get_steps()
    + GET_ACTION.get_steps()
    + RUN_ACTION.get_steps(),
)
