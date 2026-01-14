# Système de Gestion de Restaurant

Application web Django pour la gestion complète d'un restaurant avec prise de commande via tablettes.

## 📋 Fonctionnalités

- **Gestion des rôles** : Table, Serveur, Cuisinier, Comptable, Administrateur
- **Prise de commande** : Via tablettes sur chaque table
- **Gestion du menu** : Ajout, modification et désactivation des plats
- **Suivi des commandes** : Statuts en temps réel (en attente, servie, payée)
- **Gestion des paiements** : Validation physique et enregistrement
- **Caisse** : Suivi du solde avec paiements et dépenses
- **Gestion des dépenses** : Enregistrement avec vérification du solde

## 🚀 Installation

### Prérequis

- Python 3.10+
- MySQL 8.0+
- Node.js 18+ (pour Tailwind CSS)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone https://github.com/Ibrvhima/restaurant_management.git
cd restaurant_management
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données MySQL**
```sql
CREATE DATABASE restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'restaurant_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON restaurant_db.* TO 'restaurant_user'@'localhost';
FLUSH PRIVILEGES;
```

5. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

6. **Installer les dépendances Node.js**
```bash
npm install
```

7. **Compiler Tailwind CSS**
```bash
# Mode développement (avec watch)
npm run dev

# Mode production
npm run build
```

8. **Appliquer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

9. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

10. **Créer l'instance de la caisse**
```bash
python manage.py shell
>>> from payments.models import Caisse
>>> Caisse.get_instance()
>>> exit()
```

11. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : `http://localhost:8000`

## 📁 Structure du projet

```
restaurant_management/
├── core/                   # Configuration principale
├── accounts/               # Gestion des utilisateurs et authentification
├── restaurant/             # Tables et plats
├── orders/                 # Paniers et commandes
├── payments/               # Paiements et caisse
├── expenses/               # Dépenses
├── templates/              # Templates globaux
├── static/                 # Fichiers statiques
│   └── css/
│       ├── input.css       # Source Tailwind
│       └── output.css      # CSS compilé
└── media/                  # Fichiers uploadés (images des plats)
```

## 👥 Rôles et permissions

### Table (Rtable)
- Consulter les plats
- Ajouter au panier
- Valider une commande

### Serveur (Rserveur)
- Voir toutes les tables
- Consulter les commandes
- Valider les commandes comme servies
- Valider les paiements

### Cuisinier (Rcuisinier)
- Ajouter des plats
- Modifier des plats
- Activer/désactiver des plats

### Comptable (Rcomptable)
- Consulter les commandes
- Voir les paiements
- Consulter le solde de la caisse
- Enregistrer des dépenses

### Administrateur (Radmin)
- Accès complet à toutes les fonctionnalités
- Suppression de données
- Gestion des utilisateurs

## 🔐 Authentification

- **Login** : Minimum 6 caractères alphanumériques
- **Mot de passe** : Lettres, chiffres et caractères spéciaux

Exemples de login :
- `TABLE001`
- `SERV123`
- `ADMIN001`

## 💳 Processus de paiement

1. Client valide son panier → Commande créée (statut: en attente)
2. Serveur sert les plats → Statut: servie
3. Client paie physiquement
4. Serveur valide le paiement → Statut: payée
5. Montant ajouté automatiquement à la caisse

## 💰 Gestion de la caisse

- **Paiement validé** : +Montant
- **Dépense enregistrée** : -Montant
- Une dépense ne peut être enregistrée que si le solde est suffisant

## 🎨 Tailwind CSS

Le projet utilise Tailwind CSS pour le design. Les commandes disponibles :

```bash
# Mode développement (recompilation automatique)
npm run dev

# Mode production (minifié)
npm run build
```

## 🔧 Commandes utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer les tests
python manage.py test
```

## 📊 Fonctionnalités bonus

- Tableau de bord avec statistiques
- Export des données en Excel
- Impression des données en PDF
- Mise à jour automatique quotidienne de la caisse
- Envoi par email à l'admin

## 🛠️ Technologies utilisées

- **Backend** : Django 5.0
- **Frontend** : Django Templates + Tailwind CSS
- **Base de données** : MySQL 8.0
- **Images** : Pillow
- **Export Excel** : openpyxl
- **Export PDF** : ReportLab

## 🌐 Déploiement

### Production (Vercel)
L'application est déployée automatiquement sur Vercel :
**https://restaurant-management.vercel.app**

### Mise à jour
Chaque `git push` sur la branche `main` déploie automatiquement la dernière version.

### Configuration Vercel
- Runtime : Python 3.13
- Serveur : Gunicorn
- Base de données : PostgreSQL (Vercel)
- Fichiers statiques : Optimisés automatiquement

## 👨‍💻 Support

Pour toute question ou problème, veuillez créer une issue dans le repository.
