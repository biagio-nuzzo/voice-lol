import os

# Bark TTS
from bark import generate_audio as generate_audio
import numpy as np
import scipy.io.wavfile as wav
import torch

# Settings
from settings import OVERWRITE, SPEECHES_DIR

# Se è disponibile la GPU MPS, usiamola
device = "mps" if torch.backends.mps.is_available() else "cpu"

# Assicuriamoci che la cartella `speeches/` esista
os.makedirs(SPEECHES_DIR, exist_ok=True)


def generate_audio_bark(text: str, filename: str):
    """
    Genera un file audio utilizzando Bark con voce femminile italiana e qualità ottimizzata.

    Args:
        text (str): Il testo da convertire in audio.
        filename (str): Nome del file audio (senza estensione).
    """
    output_path = f"speeches/{filename}.wav"

    # Controlla se il file esiste già
    if os.path.exists(output_path) and not OVERWRITE:
        print(f"🔹 Il file '{output_path}' esiste già, salto la generazione.")
        return output_path

    print(
        f"🎙 Generazione audio con Bark (voce femminile italiana) su {device}: {output_path}"
    )

    # Sposta il modello su MPS se disponibile
    torch.set_default_device(device)

    # Genera l'audio con voce femminile italiana
    audio_array = generate_audio(text, history_prompt="v2/it_speaker_2")

    # Normalizza l'audio per evitare distorsioni
    audio_array = np.clip(audio_array, -1, 1)

    # Salva il file WAV in alta qualità (32-bit float)
    wav.write(output_path, rate=24000, data=(audio_array * 32767).astype(np.int16))

    print(f"✔️ Audio salvato: {output_path}")
    return output_path
