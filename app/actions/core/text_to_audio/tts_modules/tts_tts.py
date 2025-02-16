import os

# TTS
from TTS.api import TTS

# Settings
from settings import MODEL_DIR, TTS_MODEL_NAME, OVERWRITE, SPEECHES_DIR


# Assicuriamoci che la cartella `speeches/` esista
os.makedirs(SPEECHES_DIR, exist_ok=True)


# Funzione per generare l'audio
def generate_audio_tts(text: str, filename: str):
    """
    Genera un file audio da un testo e lo salva nella cartella `speeches/`.

    Args:
        text (str): Il testo da convertire in audio.
        filename (str): Nome del file audio (senza estensione).
    """
    output_path = os.path.join(SPEECHES_DIR, f"{filename}.wav")

    # Controlla se il file esiste già
    if os.path.exists(output_path) and not OVERWRITE:
        print(f"🔹 Il file '{output_path}' esiste già, salto la generazione.")
        return output_path

    # Controlla se il modello è già scaricato
    model_path = os.path.join(MODEL_DIR, TTS_MODEL_NAME.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"📥 Modello non trovato. Download in corso di {TTS_MODEL_NAME}...")
        tts = TTS(TTS_MODEL_NAME)
        print("✅ Modello scaricato con successo!")
    else:
        print("✅ Modello già presente. Procedo con la sintesi vocale...")
        tts = TTS(TTS_MODEL_NAME)

    # Genera l'audio e salva il file
    print(f"🎙 Generazione audio: {output_path}")
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speed=1.0,  # Evita rallentamenti che possono distorcere la voce
        noise_scale=1.5,  # Riduce la "roboticità"
        noise_w=0.1,  # Mantiene una voce più pulita
        length_scale=1.2,  # Mantiene un ritmo naturale
    )
    print(f"✔️ Audio salvato: {output_path}")
    return output_path
