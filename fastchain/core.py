from typing import Any, List, Type, Callable, Union
import importlib


class ActionStep:
    """
    Rappresenta uno step di una Action.
    """

    def __init__(
        self,
        function: Union[str, Callable],
        input_type: Type = None,
        output_type: Type = None,
    ):
        self.function = function
        self.input_type = input_type
        self.output_type = output_type

    def __repr__(self):
        return f"ActionStep(function={self.function}, input_type={self.input_type}, output_type={self.output_type})"


class Action:
    """
    Classe base per tutte le Action.
    """

    def __init__(
        self,
        name: str,
        description: str,
        verbose_name: str,
        steps: List[Union[ActionStep, dict]],
        input_action: bool = False,
        stepBuilder: Type[ActionStep] = ActionStep,
    ):
        self.name = name
        self.description = description
        self.verbose_name = verbose_name
        self.input_action = input_action
        self.stepBuilder = stepBuilder

        # Convertiamo gli step in oggetti ActionStep se non lo sono già
        self.steps = [
            step if isinstance(step, ActionStep) else self.stepBuilder(**step)
            for step in steps
        ]

    def execute(self, input_data: Any = None) -> Any:
        """
        Esegue gli step in sequenza, propagando l'output di uno step come input del successivo.
        """
        print(f"Esecuzione della action: {self.name}")
        data = input_data
        for step in self.steps:
            function = (
                step.function
                if callable(step.function)
                else self._resolve_function(step.function)
            )
            if function:
                try:
                    # Controlliamo se la funzione accetta parametri
                    if step.input_type is None:
                        data = function()
                    else:
                        data = function(data)
                except TypeError as e:
                    raise ValueError(f"Errore eseguendo {step.function}: {e}")
        return data

    def _resolve_function(self, function_name: str):
        """
        Risolve il nome della funzione in una funzione eseguibile se è stata passata come stringa.
        """
        try:
            module_name, func_name = function_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, func_name, None)
        except (ValueError, ModuleNotFoundError, AttributeError):
            return None

    def __repr__(self):
        return f"Action(name={self.name}, description={self.description}, verbose_name={self.verbose_name}, steps={self.steps}, input_action={self.input_action})"
