#!/bin/bash
# Script de déploiement pour Vercel

echo "🚀 Déploiement Django sur Vercel"

# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer un superutilisateur (optionnel)
# python manage.py createsuperuser

echo "✅ Déploiement terminé !"
