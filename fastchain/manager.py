from app.action_registry import ACTION_REGISTRY
from typing import Any


class FastChainManager:
    """Gestisce l'esecuzione delle actions di FastChain."""

    @staticmethod
    def get_available_actions():
        """Restituisce la lista delle azioni registrate."""
        return list(ACTION_REGISTRY.keys())

    @staticmethod
    def run_action(action_name: str, input_data: Any = None):
        """Esegue un'azione se esiste nel registro."""
        action = ACTION_REGISTRY.get(action_name)

        if not action:
            print(f"[ERROR] Action '{action_name}' non trovata nel registro!")
            return None

        print(f"\n[MANAGER] Avvio action '{action_name}'...")
        return action.execute(input_data)
