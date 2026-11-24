#!/bin/bash
# Lanceur macOS / Linux de la plateforme EXETAT
cd "$(dirname "$0")" || exit 1
echo "=== Plateforme EXETAT ==="

# 1) Cherche un vrai Python 3.10+ : d'abord le Python officiel (python.org), puis Homebrew, puis le PATH.
PY=""
for c in /Library/Frameworks/Python.framework/Versions/3.*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then
    # Le python3 d'Apple (/usr/bin/python3) dépend de Xcode : on l'ignore si Xcode n'est pas prêt.
    if "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >/dev/null 2>&1; then PY="$c"; break; fi
  fi
done

if [ -z "$PY" ]; then
  echo
  echo "Aucun Python 3.10+ utilisable n'a été trouvé sur cet ordinateur."
  echo "(Le python3 fourni par Apple dépend de Xcode et n'est pas prêt.)"
  echo
  echo "À faire une seule fois : installer le Python officiel, puis relancer ce fichier."
  echo "   https://www.python.org/downloads/macos/   (bouton « Latest Python 3 Release », fichier .pkg)"
  echo
  open "https://www.python.org/downloads/macos/" 2>/dev/null
  read -r -p "Entrée pour fermer." ; exit 1
fi

echo "Python : $("$PY" --version 2>&1)"
"$PY" lancer.py
echo
read -r -p "Plateforme arrêtée. Entrée pour fermer."
