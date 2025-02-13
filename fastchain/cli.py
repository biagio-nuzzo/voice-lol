#!/usr/bin/env python

import sys
import os
import subprocess


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run" or sys.argv[2] != "app":
        print("Uso corretto: fastchain run app")
        sys.exit(1)

    # Percorso dell'applicazione
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_main = os.path.join(project_root, "..", "app", "main.py")

    if not os.path.exists(app_main):
        print("Errore: Il file 'app/main.py' non esiste!")
        sys.exit(1)

    # Avvia l'applicazione
    subprocess.run(["python", app_main])


if __name__ == "__main__":
    main()
