@echo off
echo 🚀 Installation des dépendances ColepsBot...

set "VENV_ACTIVATE=Scripts\activate"
set "VENV_ACTIVATE_PS=Scripts\Activate.ps1"

REM Teste si on est dans cmd classique
if "%ComSpec%"=="%SystemRoot%\system32\cmd.exe" (
	if exist %VENV_ACTIVATE% (
		call %VENV_ACTIVATE%
		FOR /F "tokens=*" %%i IN (requirements.txt) DO (
			echo Installing %%i...
			pip install %%i
		)
		echo All packages installed.
		REM Lancement du bot via l'interface graphique
		python main.py
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
		echo Puis lancez ce script à nouveau.
	) else (
		echo [ERREUR] Environnement virtuel non trouvé dans Scripts\Activate.ps1
		echo Créez-le avec : python -m venv .
	)
	pause
	exit /b 1

)
pause