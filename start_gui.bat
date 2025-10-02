@echo off
REM Script pour installer les dépendances et lancer l'interface graphique du bot

REM Activer l'environnement virtuel
if exist Scripts\activate (
    call Scripts\activate
) else (
    echo [ERREUR] Environnement virtuel non trouvé dans Scripts\activate
    echo Créez-le avec : python -m venv .
    pause
    exit /b 1
)

REM Installer les dépendances
pip install -r "installation guide\requirements.txt"
if errorlevel 1 (
    echo [ERREUR] L'installation des dépendances a échoué.
    pause
    exit /b 1
)

REM Lancer l'interface graphique du bot
python gui.py

pause
