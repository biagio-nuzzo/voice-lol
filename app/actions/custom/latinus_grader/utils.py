from .constants import EVALUATION_MATRIX

def generate_section_prompt(section_name):
    """
    Genera un testo strutturato per il pre-prompt basato sulla sezione specificata.

    Args:
        section_name (str): Nome della sezione da estrarre ("Conoscenze", "Abilità" o "Competenze").
        evaluation_matrix (dict): Struttura JSON contenente la matrice di valutazione.

    Returns:
        str: Testo strutturato con il nome della sezione, la sua descrizione e i dettagli per ogni voto.
    """
    # Trova la sezione richiesta (ignorando differenze di maiuscole/minuscole)
    section = next((s for s in EVALUATION_MATRIX["sections"] 
                    if s["name"].lower() == section_name.lower()), None)
    if section is None:
        raise ValueError(f"Sezione '{section_name}' non trovata nella matrice di valutazione.")

    # Costruisci il testo strutturato
    output = f"Sezione: {section['name']}\n"
    output += f"Descrizione: {section['description']}\n\n"
    output += "Valutazioni:\n"
    for voto in EVALUATION_MATRIX["columns"]:
        cell_text = section["cells"].get(voto, "")
        output += f"- {voto}: {cell_text}\n"
    
    return output