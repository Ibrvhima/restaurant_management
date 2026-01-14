#!/bin/bash

# Script de démarrage rapide pour le projet Restaurant Management
# Ce script doit être exécuté depuis le répertoire racine du projet

echo "========================================="
echo "Restaurant Management System - Démarrage"
echo "========================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé."
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
if [ ! -f "venv/bin/django-admin" ]; then
    echo "Installation des dépendances Python..."
    pip install -r requirements.txt
    echo "✅ Dépendances installées."
fi

# Vérifier si Node modules sont installés
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances Node.js..."
    npm install
    echo "✅ Dépendances Node.js installées."
fi

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé."
    echo "Copie du fichier .env.example vers .env..."
    cp .env.example .env
    echo "⚠️  Veuillez configurer le fichier .env avec vos paramètres."
    read -p "Appuyez sur Entrée pour continuer..."
fi

# Appliquer les migrations si nécessaire
echo "Vérification des migrations..."
python manage.py migrate --check 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Application des migrations..."
    python manage.py makemigrations
    python manage.py migrate
    echo "✅ Migrations appliquées."
fi

# Compiler Tailwind CSS
echo "Compilation de Tailwind CSS..."
npm run build
echo "✅ CSS compilé."

# Créer la caisse si elle n'existe pas
echo "Vérification de la caisse..."
python manage.py shell -c "from payments.models import Caisse; Caisse.get_instance()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Caisse initialisée."
fi

echo ""
echo "========================================="
echo "✅ Configuration terminée!"
echo "========================================="
echo ""
echo "Pour démarrer l'application, ouvrez 2 terminaux :"
echo ""
echo "Terminal 1 (Django):"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 (Tailwind - optionnel en dev):"
echo "  npm run dev"
echo ""
echo "Accès : http://localhost:8000"
echo "Admin : http://localhost:8000/admin"
echo ""
