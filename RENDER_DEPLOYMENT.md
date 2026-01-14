# Guide de Déploiement sur Render

## 🚀 Déploiement sur Render

### Étape 1: Préparer le Repository

Le projet est déjà configuré pour Render avec :
- `render.yaml` : Configuration du service web
- `render_build.sh` : Script de build
- `settings_production.py` : Settings optimisés pour Render

### Étape 2: Créer un Compte Render

1. Allez sur [render.com](https://render.com)
2. Créez un compte avec GitHub
3. Autorisez Render à accéder à vos repositories

### Étape 3: Créer le Service Web

1. **Connectez votre repository** :
   - Cliquez sur "New +" → "Web Service"
   - Sélectionnez `Ibrvhima/restaurant_management`
   - Choisissez la branche `main`

2. **Configuration du service** :
   ```
   Name: restaurant-management
   Environment: Python 3
   Region: Europe (Paris)
   Branch: main
   Root Directory: (laisser vide)
   Runtime: Python 3.13
   Build Command: bash render_build.sh
   Start Command: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
   ```

3. **Variables d'environnement** :
   ```
   DJANGO_SETTINGS_MODULE: core.settings_production
   SECRET_KEY: (généré automatiquement)
   DEBUG: False
   ```

### Étape 4: Créer la Base de Données

1. **Ajouter une base de données PostgreSQL** :
   - Cliquez sur "New +" → "PostgreSQL"
   - Name: `restaurant-db`
   - Database Name: `restaurant_management`
   - User: `postgres`
   - Plan: Free

2. **Connecter la base de données** :
   - Une fois créée, Render générera un `DATABASE_URL`
   - Ajoutez cette URL aux variables d'environnement du service web

### Étape 5: Déployer

1. **Déclencher le déploiement** :
   - Render détectera automatiquement les changements
   - Le build commencera automatiquement

2. **Suivre le déploiement** :
   - Watch les logs en temps réel
   - Le déploiement prend 3-5 minutes

### Étape 6: Vérifier le Déploiement

1. **URL de l'application** :
   - Render vous donnera une URL comme : `https://restaurant-management.onrender.com`

2. **Tests à effectuer** :
   - Page d'accueil accessible
   - Login admin fonctionnel
   - Création d'un utilisateur test
   - Test des rôles et permissions

## 🔧 Configuration Avancée

### Variables d'Environnement Complètes

```bash
# Django
DJANGO_SETTINGS_MODULE=core.settings_production
SECRET_KEY=votre-clé-secrète
DEBUG=False

# Base de données (généré automatiquement par Render)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password
```

### Personnalisation du Domaine

1. **Domaine personnalisé** :
   - Dans les settings du service → "Custom Domains"
   - Ajoutez votre domaine (ex: `restaurant.votredomaine.com`)
   - Configurez le DNS selon les instructions Render

2. **SSL automatique** :
   - Render génère automatiquement un certificat SSL
   - HTTPS est activé par défaut

## 📊 Monitoring et Logs

### Logs en Temps Réel

1. **Logs de build** :
   - Onglet "Logs" → "Build Logs"
   - Vérifiez les erreurs de build

2. **Logs de l'application** :
   - Onglet "Logs" → "Service Logs"
   - Surveillez les erreurs runtime

### Monitoring

1. **Métriques** :
   - CPU, mémoire, réseau
   - Temps de réponse
   - Taux d'erreur

2. **Alertes** :
   - Configurez des alertes email
   - Surveillance 24/7

## 🔄 Mises à Jour

### Déploiement Automatique

Chaque `git push` sur la branche `main` déclenche :
1. Build automatique
2. Migration de la base de données
3. Redémarrage du service
4. Health check

### Déploiement Manuel

1. **Forcer un redeploy** :
   - Bouton "Manual Deploy" dans le dashboard
   - Choisissez la branche et le commit

2. **Rollback** :
   - Bouton "Deploy" → choisissez un commit précédent
   - Restauration instantanée

## 🐛 Dépannage

### Problèmes Communs

1. **Erreur de build** :
   - Vérifiez `requirements.txt`
   - Confirmez les variables d'environnement
   - Regardez les logs de build

2. **Erreur de base de données** :
   - Vérifiez `DATABASE_URL`
   - Confirmez que la DB est connectée
   - Testez la connexion manuellement

3. **Erreur 500** :
   - Vérifiez les logs du service
   - Confirmez `DEBUG=False` en production
   - Vérifiez les permissions des fichiers

### Commandes Utiles

```bash
# Débugger localement avec les settings production
export DJANGO_SETTINGS_MODULE=core.settings_production
export DATABASE_URL=postgresql://user:pass@host:port/db
python manage.py migrate
python manage.py runserver
```

## 📈 Performance

### Optimisations

1. **Base de données** :
   - Indexation automatique avec PostgreSQL
   - Connection pooling inclus

2. **Static files** :
   - Servis par CDN Render
   - Compression automatique

3. **Caching** :
   - Redis disponible (plan payant)
   - Cache des templates activé

## 💰 Coûts

### Plan Free
- 750 heures/mois
- 100GB de bande passante
- Base de données PostgreSQL gratuite
- Custom domain

### Plan Pro (recommandé pour production)
- Pas de limite d'heures
- Plus de bande passante
- Support prioritaire
- ~$7/mois

## 🎯 Conclusion

Render offre une solution de déploiement simple et robuste pour Django avec :
- **CI/CD intégré**
- **Base de données PostgreSQL**
- **SSL automatique**
- **Monitoring inclus**
- **Scaling facile**

Votre Restaurant Management System est prêt pour la production sur Render ! 🚀
