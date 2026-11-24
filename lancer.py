"""Lanceur : démarre la plateforme et ouvre le navigateur. Utilisé par les fichiers « Lancer EXETAT »."""
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ICI = Path(__file__).resolve().parent
os.chdir(ICI)
PORT = int(os.environ.get("EXETAT_PORT", "8000"))


def port_libre(p):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", p)) != 0


VENV = ICI / ".venv"


def python_venv():
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def installer_si_besoin():
    """Crée un environnement Python isolé (.venv) et y installe les composants, puis se relance dedans.
    Évite les refus du Python système (macOS, Linux : « externally-managed-environment »)."""
    if sys.prefix != str(VENV):
        if not python_venv().exists():
            print("Première installation (une seule fois, réseau requis) : création de l'environnement…")
            import venv
            venv.EnvBuilder(with_pip=True).create(VENV)
            subprocess.check_call([str(python_venv()), "-m", "pip", "install", "-q", "--upgrade", "pip"])
            subprocess.check_call([str(python_venv()), "-m", "pip", "install", "-q", "-r", "requirements.txt"])
            print("Composants installés.")
        os.execv(str(python_venv()), [str(python_venv()), str(ICI / "lancer.py")])
    try:
        import fastapi, uvicorn, anthropic, dotenv  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])


def preparer_base():
    from app.db import preparer
    preparer()
    if not (ICI / ".env").exists():
        (ICI / ".env").write_text((ICI / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
        print("Fichier .env créé : ouvrez-le pour coller votre clé API (génération automatique).")


def main():
    installer_si_besoin()
    preparer_base()
    url = f"http://127.0.0.1:{PORT}/"
    if not port_libre(PORT):
        print("La plateforme tourne déjà : ouverture du navigateur.")
        webbrowser.open(url)
        return
    import uvicorn

    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    print(f"\nPlateforme EXETAT démarrée : {url}\nLaissez cette fenêtre ouverte. Fermez-la pour arrêter.\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print("\nErreur :", e)
        input("\nAppuyez sur Entrée pour fermer.")
