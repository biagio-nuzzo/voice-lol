from fastchain.core import Action
from app.actions.core.get_action import GET_ACTION
from app.actions.core.run_action import RUN_ACTION

START_AGENT = Action(
    name="START_AGENT",
    description="Concatena GET_ACTION e RUN_ACTION: acquisisce il nome dell'azione e la esegue.",
    verbose_name="Avvio Agente",
    core=True,
    steps=GET_ACTION.get_steps() + RUN_ACTION.get_steps(),
)
