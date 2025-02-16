# FastChain
from fastchain.core import Action

# Actions
from app.actions.core.show_output import SHOW_OUTPUT


class GetListOfActions:
    def execute(self):
        """
        Restituisce la lista di tutte le azioni disponibili formattata in modo leggibile.
        """
        from fastchain.manager import FastChainManager

        actions = FastChainManager.get_available_actions()
        # Per ogni action, creiamo una stringa formattata con indice, nome, descrizione e verbose_name.
        formatted_actions = "\n\n".join(
            [
                f"{index}. Nome: {action['name']}\n"
                f"   Descrizione: {action['description']}\n"
                for index, action in enumerate(actions, 1)
            ]
        )
        return {
            "config": {
                "title": "Lista Azioni",
                "size": "medium",
            },
            "text": formatted_actions,
        }


GET_LIST_OF_ACTIONS = Action(
    name="GET_LIST_OF_ACTIONS",
    description="Restituisce la lista di tutte le azioni disponibili.",
    verbose_name="Lista Azioni",
    steps=[
        {
            "function": GetListOfActions().execute,
            "input_type": None,
            "output_type": dict,
        }
    ]
    + SHOW_OUTPUT.get_steps(),
)
