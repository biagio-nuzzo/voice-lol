from app.action_registry import ACTION_REGISTRY
from typing import Any


class FastChainManager:
    """Gestisce l'esecuzione delle actions di FastChain."""

    @staticmethod
    def get_available_actions(exclude_core=True):
        """
        Restituisce una lista di dizionari contenenti 'name', 'description' e 'verbose_name'
        per ogni action registrata. Se 'exclude_core' è True, le action con core=True vengono escluse.
        """
        return [
            {
                "name": action.name,
                "description": action.description,
                "verbose_name": action.verbose_name,
            }
            for action in ACTION_REGISTRY.values()
            if not (exclude_core and getattr(action, "core", False))
        ]

    @staticmethod
    def run_action(action_name: str, input_data: Any = None):
        """Esegue un'azione se esiste nel registro, verificando che l'input fornito
        corrisponda al tipo richiesto dall'action."""
        action = ACTION_REGISTRY.get(action_name)
        if not action:
            print(f"[ERROR] Action '{action_name}' non trovata nel registro!")
            return None

        # Otteniamo il primo step dell'action, che ora è un oggetto ActionStep
        step = action.steps[0] if action.steps else None
        # Utilizziamo getattr per ottenere l'attributo 'input_type' con default None
        expected_input_type = getattr(step, "input_type", None)

        # Se l'azione richiede un input specifico...
        if expected_input_type is not None:
            # ... e nessun input è stato fornito, interrompiamo l'esecuzione.
            if input_data is None:
                print(
                    f"[ERROR] L'azione '{action_name}' richiede un input di tipo {expected_input_type.__name__}, ma nessun input è stato fornito!"
                )
                return None
            # ... e l'input fornito non è del tipo corretto.
            if not isinstance(input_data, expected_input_type):
                print(
                    f"[ERROR] L'azione '{action_name}' richiede un input di tipo {expected_input_type.__name__}, ma è stato fornito un input di tipo {type(input_data).__name__}!"
                )
                return None

        print(f"\n[MANAGER] Avvio action '{action_name}'...")
        return action.execute(input_data)
