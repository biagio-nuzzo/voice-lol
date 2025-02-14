# Built-in
import re
import unicodedata

# Audio
import simpleaudio as sa


# Funzione per riprodurre l'audio
def play_audio(audio_file):
    print(f"▶️ Riproduzione audio: {audio_file}")
    wave_obj = sa.WaveObject.from_wave_file(audio_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


# Funzione per pulire il testo prima di convertirlo in audio
def clean_text_for_tts(text):
    """
    Pulisce il testo prima di convertirlo in audio.
    Rimuove caratteri non supportati, simboli speciali, sostituisce numeri con parole e assicura una lunghezza minima.
    """
    # Normalizza il testo rimuovendo caratteri speciali Unicode
    text = unicodedata.normalize("NFKD", text)

    # Rimuove parentesi graffe e altri caratteri non supportati
    text = re.sub(r"[{}\[\]<>]", "", text)

    # Sostituisce il simbolo % con "percento"
    text = text.replace("%", " percento")

    # Sostituisce simboli comuni con testo leggibile
    replacements = {
        "$": " dollari",
        "€": " euro",
        "&": " e ",
        "@": " chiocciola ",
        "#": " hashtag ",
        "*": "  ",
        "~": " tilde ",
        "^": " elevato alla ",
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    # Rimuove caratteri non alfabetici isolati (ad esempio, caratteri di controllo o simboli strani)
    text = re.sub(r"[^a-zA-Z0-9À-ÿ.,!?()'\"\s]", "", text)

    # Rimuove spazi extra
    text = re.sub(r"\s+", " ", text).strip()

    # Assicura una lunghezza minima per evitare errori di sintesi vocale
    if len(text) < 50:
        text += " Questo è un messaggio di riempimento per garantire una lunghezza sufficiente."

    return text
