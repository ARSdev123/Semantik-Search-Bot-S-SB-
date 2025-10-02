pause
@echo off
echo 🚀 Démarrage du ColepsBot API...

REM Détection de l'environnement (cmd ou PowerShell)
set "VENV_ACTIVATE=Scripts\activate"
set "VENV_ACTIVATE_PS=Scripts\Activate.ps1"

REM Teste si on est dans cmd classique
if "%ComSpec%"=="%SystemRoot%\system32\cmd.exe" (
	if exist %VENV_ACTIVATE% (
		call %VENV_ACTIVATE%
		uvicorn fastapi_main:app --host 0.0.0.0 --port 8000 --reload
	) else (
		echo [ERREUR] Environnement virtuel non trouvé dans Scripts\activate
		echo Créez-le avec : python -m venv .
		pause
		exit /b 1
	)
) else (
	if exist %VENV_ACTIVATE_PS% (
		echo Pour activer l'environnement virtuel sous PowerShell, exécutez :
		echo .\Scripts\Activate.ps1
		echo Puis lancez :
		echo uvicorn fastapi_main:app --host 0.0.0.0 --port 8000 --reload
	) else (
		echo [ERREUR] Environnement virtuel non trouvé dans Scripts\Activate.ps1
		echo Créez-le avec : python -m venv .
	)
	pause
	exit /b 1
)