@echo off
REM Script de démarrage rapide pour le projet Restaurant Management (Windows)
REM Ce script doit être exécuté depuis le répertoire racine du projet

echo =========================================
echo Restaurant Management System - Demarrage
echo =========================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo Environnement virtuel non trouve.
    echo Creation de l'environnement virtuel...
    python -m venv venv
    echo Environnement virtuel cree.
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier si les dépendances sont installées
if not exist "venv\Scripts\django-admin.exe" (
    echo Installation des dependances Python...
    pip install -r requirements.txt
    echo Dependances installees.
)

REM Vérifier si Node modules sont installés
if not exist "node_modules" (
    echo Installation des dependances Node.js...
    npm install
    echo Dependances Node.js installees.
)

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo Fichier .env non trouve.
    echo Copie du fichier .env.example vers .env...
    copy .env.example .env
    echo Veuillez configurer le fichier .env avec vos parametres.
    pause
)

REM Appliquer les migrations
echo Verification des migrations...
python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo Application des migrations...
    python manage.py makemigrations
    python manage.py migrate
    echo Migrations appliquees.
)

REM Compiler Tailwind CSS
echo Compilation de Tailwind CSS...
npm run build
echo CSS compile.

REM Créer la caisse si elle n'existe pas
echo Verification de la caisse...
python manage.py shell -c "from payments.models import Caisse; Caisse.get_instance()" >nul 2>&1
if not errorlevel 1 (
    echo Caisse initialisee.
)

echo.
echo =========================================
echo Configuration terminee!
echo =========================================
echo.
echo Pour demarrer l'application, ouvrez 2 terminaux :
echo.
echo Terminal 1 (Django):
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Terminal 2 (Tailwind - optionnel en dev):
echo   npm run dev
echo.
echo Acces : http://localhost:8000
echo Admin : http://localhost:8000/admin
echo.
pause
