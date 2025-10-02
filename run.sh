#!/bin/bash
echo "🚀 Démarrage du ColepsBot API..."


# Activer l'environnement virtuel (cherche venv, env ou Scripts)
if [ -f "venv/bin/activate" ]; then
	source venv/bin/activate
elif [ -f "env/bin/activate" ]; then
	source env/bin/activate
elif [ -f "Scripts/activate" ]; then
	source Scripts/activate
else
	echo "⚠️  Aucun environnement virtuel trouvé. Pensez à en créer un avec 'python3 -m venv venv' ou 'python3 -m venv env' !"
fi

# Lancer le serveur sur toutes les interfaces (accessible depuis le réseau)
uvicorn fastapi_main:app --host 0.0.0.0 --port 8000 --reload
