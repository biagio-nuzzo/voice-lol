from typing import Any, List, Type, Callable, Union
import importlib
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QEventLoop


class ActionStep:
    """
    Rappresenta uno step di una Action.
    """

    def __init__(
        self,
        function: Union[str, Callable],
        input_type: Type = None,
        output_type: Type = None,
        thread: bool = False,  # Se True, questo step viene eseguito in un QThread
    ):
        self.function = function
        self.input_type = input_type
        self.output_type = output_type
        self.thread = thread

    def __repr__(self):
        return (
            f"ActionStep(function={self.function}, input_type={self.input_type}, "
            f"output_type={self.output_type}, thread={self.thread})"
        )


class StepWorker(QObject):
    """
    Worker per eseguire una funzione di uno step in un QThread.
    """

    finished = pyqtSignal(object)

    def __init__(self, function, input_type, data):
        super().__init__()
        self.function = function
        self.input_type = input_type
        self.data = data

    def run(self):
        try:
            result = (
                self.function() if self.input_type is None else self.function(self.data)
            )
        except Exception as e:
            result = None
            print(f"[ERROR] Errore eseguendo {self.function}: {e}")
        self.finished.emit(result)


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
        core: bool = False,
        stepBuilder: Type[ActionStep] = ActionStep,
    ):
        self.name = name
        self.description = description
        self.verbose_name = verbose_name
        self.input_action = input_action
        self.core = core
        self.stepBuilder = stepBuilder

        # Convertiamo gli step in oggetti ActionStep se non lo sono già
        self.steps = [
            step if isinstance(step, ActionStep) else self.stepBuilder(**step)
            for step in steps
        ]

    def get_steps(self) -> List[ActionStep]:
        """
        Restituisce la lista degli steps dell'Action.
        """
        return self.steps

    def execute(self, input_data: Any = None) -> Any:
        """
        Esegue gli step in sequenza.
        Aggiorna la variabile globale 'action_is_running' a True all'inizio e a False al termine.
        Se uno step ha thread=True, viene eseguito in un QThread (usando un nested event loop).
        """
        from app.ui.global_states import (
            state,
        )  # Assicurati che il file global_state.py definisca 'state'

        state["action_is_running"] = True
        print(f"\n[EXEC] Inizio esecuzione action: {self.name}")
        data = input_data

        for step in self.steps:
            function = (
                step.function
                if callable(step.function)
                else self._resolve_function(step.function)
            )

            if not function:
                print(f"[ERROR] Funzione {step.function} non trovata o non valida!")
                continue

            try:
                output_str = str(data)
                if len(output_str) > 200:
                    output_str = output_str[:200] + "..."
                print(f"[STEP] Esecuzione: {step.function} con input: {output_str}")
                if step.thread:
                    print("[STEP] Esecuzione in thread separato...")
                    data = self._execute_step_async(step, data)
                else:
                    print("[STEP] Esecuzione in thread principale...")
                    data = function() if step.input_type is None else function(data)

                # Tronca l'output a massimo 200 caratteri
                output_str = str(data)
                if len(output_str) > 200:
                    output_str = output_str[:200] + "..."
                print(f"[STEP] Output: {output_str}")
            except Exception as e:
                print(f"[ERROR] Errore eseguendo {step.function}: {e}")
                state["action_is_running"] = False
                return None
        # truncate the output to a maximum of 200 characters
        output_str = str(data)
        if len(output_str) > 200:
            output_str = output_str[:200] + "..."
        print(f"[EXEC] Fine esecuzione action: {self.name} - Risultato: {output_str}\n")
        state["action_is_running"] = False
        return data

    def _execute_step_async(self, step: ActionStep, data: Any) -> Any:
        """
        Esegue uno step in modo asincrono in un QThread e attende il risultato
        senza bloccare la UI (grazie a un nested event loop).
        """
        loop = QEventLoop()
        result_container = {}

        worker = StepWorker(step.function, step.input_type, data)
        thread = QThread()
        worker.moveToThread(thread)
        worker.finished.connect(
            lambda result: (result_container.update({"result": result}), loop.quit())
        )
        thread.started.connect(worker.run)
        thread.start()
        loop.exec_()  # Attende il segnale finished
        thread.quit()
        thread.wait()
        return result_container.get("result")

    def _resolve_function(self, function_name: str):
        """Risolve il nome della funzione e restituisce un riferimento eseguibile."""
        try:
            module_name, func_name = function_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name, None)
            if func is None:
                print(
                    f"[ERROR] Funzione {function_name} non trovata nel modulo {module_name}"
                )
            return func
        except (ValueError, ModuleNotFoundError, AttributeError) as e:
            print(f"[ERROR] Errore nel caricamento di {function_name}: {e}")
            return None

    def __repr__(self):
        return (
            f"Action(name={self.name}, description={self.description}, verbose_name={self.verbose_name}, "
            f"steps={self.steps}, input_action={self.input_action}, thread={self.thread})"
        )
