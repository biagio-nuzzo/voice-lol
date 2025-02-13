from app.action_registry import ACTION_REGISTRY


class FastChainManager:
    """
    Classe per la gestione delle actions di FastChain.
    """

    @staticmethod
    def get_available_actions():
        """
        Ritorna la lista delle actions mappate nel file action_registry.py.
        """
        return list(ACTION_REGISTRY.keys())

    @staticmethod
    def execute_action(action_name: str, input_data=None):
        """
        Esegue una action eseguendo ogni singolo step della action e restituisce il risultato finale.
        """
        action = ACTION_REGISTRY.get(action_name)
        if not action:
            raise ValueError(f"Action '{action_name}' non trovata nel registro.")
        
        result = action.execute(input_data)
        return result  # ✅ Ora ritorna il valore dell'ultima esecuzione

