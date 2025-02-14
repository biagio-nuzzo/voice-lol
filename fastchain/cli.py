import sys
import os
import zipfile
import subprocess

ZIP_NAME = "fastchain_project.zip"

EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "venv",
    "coqui",
    ".env",
    ".vscode",
    ".idea",
    "*.sublime-workspace",
    "logs",
    "*.log",
    "data/*.json",
    "models",
    "lm_studio",
    "*.bin",
    "data/speeches",
    "*.wav",
    ".DS_Store",
    "Thumbs.db",
    "fastchain.egg-info",
]


def should_exclude(file_path):
    """Verifica se un file o una cartella devono essere esclusi dallo ZIP."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("**/") and file_path.endswith(pattern[3:]):
            return True
        elif "/" in pattern:
            if pattern in file_path:
                return True
        elif file_path.endswith(pattern):
            return True
    return False


def create_zip(zip_filename):
    """Crea un archivio ZIP escludendo i file specificati, partendo dalla root del progetto."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            # Rimuove directory escluse (esempio: __pycache__)
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path):
                    zipf.write(file_path, os.path.relpath(file_path, project_root))

    print(f"✅ Archivio creato con successo: {zip_filename}")


def delete_pycaches():
    """Elimina ricorsivamente tutte le cartelle __pycache__ dalla root del progetto."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for root, dirs, files in os.walk(project_root):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                subprocess.run(["rm", "-rf", cache_path])
                print(f"🗑️ Rimosso: {cache_path}")
    print("✅ Tutti i __pycache__ sono stati eliminati.")


def main():
    """Gestisce i comandi CLI per FastChain"""
    if len(sys.argv) < 2:
        print("Uso corretto: fastchain <comando>")
        print("Comandi disponibili:")
        print("  run app   - Avvia l'applicazione")
        print("  zip       - Crea un archivio ZIP del progetto")
        print("  clean     - Elimina tutte le cartelle __pycache__")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run" and len(sys.argv) > 2 and sys.argv[2] == "app":
        # Avvia l'applicazione
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        app_main = os.path.join(project_root, "app", "main.py")

        if not os.path.exists(app_main):
            print("Errore: Il file 'app/main.py' non esiste!")
            sys.exit(1)

        subprocess.run(["python", app_main])

    elif command == "zip":
        # Crea il file ZIP del progetto partendo dalla root
        create_zip(ZIP_NAME)

    elif command == "clean":
        # Cancella tutte le cartelle __pycache__ ricorsivamente
        delete_pycaches()

    else:
        print(f"Errore: Comando sconosciuto '{command}'")
        print(
            "Usa 'fastchain run app' per avviare l'applicazione, 'fastchain zip' per creare un archivio, o 'fastchain clean' per eliminare __pycache__."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
