import requests
import re

# Settings
from app.settings import API_URL, GEMMA

# Utils
from .utils import generate_section_prompt

# Import della nuova Action dal framework
from fastchain.core import Action


class TestInput:
    def execute(self):
        """
        Ritorna il dizionario di configurazione per il dialogo che raccoglie i dati necessari:
          - destinatario: indirizzo email del destinatario (campo piccolo)
          - corpo: contenuto della mail (campo grande)
        """
        return {
            "latin_version": """Inter montes et flumina antiqui viri ex urbe remota peregrinabantur. Sub sole calido, vates praeconabant mirabilia naturae, montium altitudines, et virides silvae. Flumina tranquilla et prateae campi, in quibus avis cantabant dulces sonos, pacem et harmoniam praebebant. Virorum animo ardenti, ad novum locum viam quaerebant, spe meliorem vitam post tristes dies. In via, sapientia veterum monumenta et opera temporis memoriae in luce veritatis recitabant.""",
            "teacher_italian_version": """Tra le montagne e i fiumi, uomini antichi provenienti da una città remota peregrinavano. Sotto il caldo sole, i vati proclamavano le meraviglie della natura, le altezze delle montagne e le foreste verdi. I fiumi tranquilli e i campi erbosi, nei quali gli uccelli intonavano dolci melodie, offrivano pace e armonia. Con spirito ardente, gli uomini cercavano la via verso un nuovo luogo, nella speranza di una vita migliore dopo giorni tristi. Lungo la strada, la sapienza degli antichi recitava monumenti e opere della memoria del tempo alla luce della verità.""",
            "student_italian_version2": """Tra le montagn e i fiumi, uomini antichi da una città lontana viaggiavano. Sotto il sole caldu, i vati proclamavano le meraviglie della natura, le alte montagne e le foreste. I fiumi e i campi, dove cantavano uccelli, offrivano una pace incerta. Gli uomini cercavano un nuovo posto, sperando in una vita mejore dopo giorni tristi. Lungo la strada, le memorie antiche si mescolavano in modo confuso.""",
            "student_italian_version": """Tra le montagne e i fiumi, uomini antichi provenienti da una città remota viaggiavano. Sotto il caldo sole, i vati proclamavano le meraviglie della natura, le imponenti montagne e le rigogliose foreste. I fiumi tranquilli e i campi erbosi, dove gli uccelli intonavano dolci melodie, offrivano una pace quasi perfetta. Con ardore, gli uomini cercavano la via per un nuovo luogo, sperando in una vita migliore dopo giorni difficili. Lungo il percorso, le antiche memorie riaffioravano, seppur con qualche imprecisione.""",
            "student_italian_version3": """Tra le montagne e i fiumi, uomini antichi provenienti da una città remota peregrinavano. Sotto il caldo sole, i vati proclamavano le meraviglie della natura, le imponenti altezze delle montagne e le lussureggianti foreste. I fiumi sereni e i campi erbosi, dove gli uccelli intonavano melodie soavi, offrivano pace e armonia. Con spirito ardente, gli uomini cercavano la via verso un nuovo luogo, sperando in una vita migliore dopo giorni tristi. Lungo il percorso, la sapienza degli antichi risuonava in monumenti e opere perfette.""",
        }


class GetKnowledgeEvaluation:
    """
    Classe per valutare le conoscenze degli studenti in base a una matrice di valutazione.
    """

    def generate_prompt(
        self,
        latin_version: str,
        teacher_italian_version: str,
        student_italian_version: str,
    ) -> str:
        """
        Genera un prompt dinamico per classificare le richieste degli utenti basato sulle azioni registrate.
        """

        prompt = f"""
            **INPUT**
            *Versione in Latino*
            Testo in Latino: "{latin_version}"
            Traduzione in Italiano del Docente: "{teacher_italian_version}"
            Traduzione in Italiano dell'Alunno: "{student_italian_version}"

            *Matrice di Valutazione*
            Il tuo compito è dare un vote alle conoscenze dell'alunno, sapendo che il voto
            viene definito usando i seguenti metri di valutazione:

            {generate_section_prompt("Conoscenze")}

            *Analizza l'input e forniscimi un voto in base alla matrice di valutazione.*
            *Il voto deve essere compreso tra 1 e 10.*
            *Rispondi con il seguente formato:{{"evaluation": "voto"}}*
            *Non aggiungere altro nella risposta se non il json richiesto*
        """

        return prompt

    def execute(self, data) -> str:
        """
        Identifica l'azione richiesta dall'utente invocando il modello LLM.
        """

        if (
            not data["latin_version"]
            or not data["teacher_italian_version"]
            or not data["student_italian_version"]
        ):
            return None

        prompt = self.generate_prompt(
            data["latin_version"],
            data["teacher_italian_version"],
            data["student_italian_version"],
        )
        payload = {
            "model": GEMMA,
            "prompt": prompt,
            "max_tokens": 8000,
            "temperature": 1.0,
        }

        response = requests.post(API_URL, json=payload)

        print("RESPONSEEE", response.json())

        if response.status_code == 200:
            data = response.json()["choices"][0]["text"]
            match = re.search(r'\{\s*"evaluation"\s*:\s*"(.*?)"\s*\}', data)
            if match:
                return match.group(1)

        print(f"Errore nella richiesta: {response.status_code}")
        return ""


GET_KNOWLEDGE_EVALUATION = Action(
    name="GET_KNOWLEDGE_EVALUATION",
    description="Valuta le conoscenze degli studenti in latino in base a una matrice di valutazione.",
    verbose_name="Valutazione delle Conoscenze in Latino",
    steps=[
        {
            "function": TestInput().execute,
            "input_type": None,
            "output_type": dict,
        },
        {
            "function": GetKnowledgeEvaluation().execute,
            "input_type": dict,
            "output_type": str,
            "thread": True,
        },
    ],
)
