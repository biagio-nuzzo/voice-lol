# Built-in
import os

# TTS
from TTS.api import TTS

# Settings
from settings import MODEL_DIR, TTS_MODEL_NAME, OVERWRITE, SPEECHES_DIR


# Assicuriamoci che la cartella SPEECHES_DIR esista
os.makedirs(SPEECHES_DIR, exist_ok=True)


def generate_audio_tts(text: str, filename: str):
    """
    Genera un file audio da un testo e lo salva nella cartella SPEECHES_DIR.

    Args:
        text (str): Il testo da convertire in audio.
        filename (str): Nome del file audio (senza estensione).

    Returns:
        str: Il percorso del file audio generato.
    """
    output_path = os.path.join(SPEECHES_DIR, f"{filename}.wav")

    # Se il file esiste già e OVERWRITE è False, uso il file esistente.
    if os.path.exists(output_path) and not OVERWRITE:
        print(f"File '{output_path}' già esistente. Uso file esistente.")
        return output_path

    model_path = os.path.join(MODEL_DIR, TTS_MODEL_NAME.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"Download del modello {TTS_MODEL_NAME} in corso...")
        tts = TTS(TTS_MODEL_NAME)
        print("Download completato.")
    else:
        print("Modello già disponibile. Avvio sintesi vocale...")
        tts = TTS(TTS_MODEL_NAME)

    print(f"Generazione audio: {output_path}")
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speed=1.0,  # Velocità standard per evitare distorsioni
        noise_scale=1.5,  # Riduce la roboticità
        noise_w=0.1,  # Mantiene una voce più pulita
        length_scale=1.2,  # Ritmo naturale
    )
    print(f"Audio salvato: {output_path}")
    return output_path
