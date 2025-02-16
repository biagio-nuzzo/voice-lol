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
        """Esegue un'azione se esiste nel registro."""
        action = ACTION_REGISTRY.get(action_name)
        if not action:
            print(f"[ERROR] Action '{action_name}' non trovata nel registro!")
            return None
        print(f"\n[MANAGER] Avvio action '{action_name}'...")
        return action.execute(input_data)
