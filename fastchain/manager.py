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
