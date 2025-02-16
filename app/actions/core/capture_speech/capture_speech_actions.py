# PyQt
from PyQt5.QtCore import QEventLoop, QTimer

# FastChain
from fastchain.core import Action

# Global States
from app.ui.global_states import state

# Capture Speech Controller
from app.actions.core.capture_speech.capture_speech_controller import (
    CaptureSpeechSingleton,
)


def start_capture_action(next_action):
    # next_action DEVE essere passato, altrimenti verrà sollevato un errore
    CaptureSpeechSingleton.get_controller().start_capture(next_action)
    print("[ACTION] start_capture_action eseguita.")


def stop_capture_action():
    controller = CaptureSpeechSingleton.get_controller()
    # Fermiamo la registrazione senza triggerare automaticamente la next action,
    # dato che lo stop verrà gestito tramite il controller e la next action è già nello state
    controller.stop_capture()
    print("[ACTION] stop_capture_action eseguita.")
    loop = QEventLoop()
    result = None

    def on_finished(text):
        nonlocal result
        result = text
        loop.quit()

    if controller.recorder_thread is not None:
        controller.recorder_thread.finished.connect(on_finished)

    QTimer.singleShot(5000, loop.quit)
    loop.exec_()

    if (
        result is None
        and controller.recorder_thread is not None
        and not controller.recorder_thread.isFinished()
    ):
        print("[DEBUG] Thread non terminato entro il timeout, forzo terminate().")
        controller.recorder_thread.terminate()
        controller.recorder_thread.wait(1000)
        result = state["speech_text"]

    print("[DEBUG] Result from thread:", result)
    return result


START_CAPTURE = Action(
    name="START_CAPTURE",
    description="Avvia la registrazione vocale.",
    verbose_name="Avvia Registrazione",
    core=True,
    steps=[
        {
            "function": start_capture_action,
            "input_type": str,
            "output_type": None,
        }
    ],
    input_action=True,
)

STOP_CAPTURE = Action(
    name="STOP_CAPTURE",
    description="Ferma la registrazione vocale e restituisce il testo registrato.",
    verbose_name="Ferma Registrazione",
    core=True,
    steps=[
        {
            "function": stop_capture_action,
            "input_type": None,
            "output_type": str,
        }
    ],
    input_action=False,
)
