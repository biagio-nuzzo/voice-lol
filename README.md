# 🎮 League of Legends AI Assistant

Questo progetto è un assistente vocale AI progettato per aiutare i giocatori di League of Legends a migliorare la loro esperienza di gioco. Grazie all'integrazione con LM Studio, Bark TTS e Vosk STT, l'assistente è in grado di:

Riconoscere comandi vocali per interagire in modo naturale con il giocatore.

Analizzare le richieste utilizzando un modello LLM locale (gemma-2-2b-instruct).

Generare risposte vocali con una voce personalizzata, fornendo informazioni utili sul gioco.

Dare suggerimenti sugli oggetti di gioco, sulle strategie e sulle meccaniche di LoL.

L'assistente è progettato per migliorare la consapevolezza del giocatore durante il game, fornendo informazioni in tempo reale senza dover consultare guide esterne

# 📌 Struttura del Progetto

Il progetto è organizzato nel seguente modo:

```
project_root/
├── main.py               # Script principale dell'assistente
├── requirements.txt      # Dipendenze del progetto
├── README.md             # Documentazione del progetto
├── __init__.py           # File di inizializzazione del progetto
├── settings.py           # File di configurazione del progetto
│
├── data/
│   ├── constants/
│   │   ├── items.py      # Dizionario con gli oggetti di LoL
│   │   ├── speeches.json # Dizionario con frasi pre-impostate da generare
│   │
│   ├── speeches/         # Cartella che contiene gli audio generati con il modello TTS
│   │   ├── ...           # Audio generati con il modello TTS
│
├── models/
│   ├── vosk-model-it/
│   │   ├── ...  # Modello Vosk per il riconoscimento vocale in italiano
│
├── tests/                # Cartella contenente i test del progetto. File con varie funzioni di test
│   ├── generate_speeches.py # Test per la generazione di audio con il modello TTS
│   ├── llm.py           # Test per l'interfacciamento con LM Studio
│   ├── speech_to_text.py # Test per il riconoscimento vocale con Vosk
│
├── tts_modules/                # Cartella contenente le funzioni per generare audio con Bark o con TTS
│   ├── bark_tts.py            # Funzione per generare audio con Bark
│   ├── tts_tts.py             # Funzione per generare audio con il modello TTS
│
├── /
├── README.md             # Documentazione del progetto
```

---

## 🚀 Come Lanciare LM Studio

Per eseguire il **modello LLM locale**, segui questi passi:

1. **Apri LM Studio** sul tuo computer.
2. **Scarica e carica il modello** `gemma-2-2b-instruct`.
   - Vai nella sezione **"Models"**, cerca `gemma-2-2b-instruct` e scaricalo.
3. **Avvia il server locale**:
   - Apri **LM Studio** e nella scheda **"Server"**, assicurati che sia attivo su `http://localhost:1234`.
4. **Verifica che sia attivo** eseguendo il comando:
   ```bash
   curl http://localhost:1234/v1/models
   ```
   Se LM Studio è attivo, dovresti vedere il nome del modello caricato.

---

## 🚀 Come Lanciare il Progetto

Per eseguire l'assistente vocale:

1. **Installa le dipendenze** (se non lo hai già fatto):

   ```bash
   pip install -r requirements.txt
   ```

2. **Avvia LM Studio** con il modello `gemma-2-2b-instruct`.

3. **Esegui lo script principale**:
   ```bash
   python main.py
   ```

Ora l'assistente vocale sarà in ascolto e potrai attivarlo con i comandi vocali! 🎤💬
