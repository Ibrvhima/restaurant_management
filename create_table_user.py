#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from restaurant.models import TableRestaurant

# Créer un utilisateur table
try:
    # Vérifier si l'utilisateur existe déjà
    user = User.objects.get(login='table1')
    print(f"L'utilisateur {user.login} existe déjà.")
except User.DoesNotExist:
    # Créer l'utilisateur
    user = User.objects.create_user(
        login='table1',
        password='table123',
        role='Rtable',
        nom='Utilisateur',
        prenom='Table 1'
    )
    print(f"Utilisateur {user.login} créé avec succès.")

# Créer une table si elle n'existe pas
try:
    table = TableRestaurant.objects.get(numero_table=1)
    print(f"La table {table.numero_table} existe déjà.")
except TableRestaurant.DoesNotExist:
    table = TableRestaurant.objects.create(
        numero_table=1,
        nombre_places=4,
        utilisateur=user,
        est_occupee=False
    )
    print(f"Table {table.numero_table} créée avec succès.")
except TableRestaurant.MultipleObjectsReturned:
    table = TableRestaurant.objects.filter(numero_table=1).first()
    print(f"Plusieurs tables trouvées, utilisation de la première.")

# Associer l'utilisateur à la table
table.utilisateur = user
table.save()

print("\n✅ UTILISATEUR TABLE CRÉÉ AVEC SUCCÈS")
print("📋 Identifiants de connexion :")
print("   Login: table1")
print("   Mot de passe: table123")
print("   Rôle: Rtable")
print("   Table: Table 1")
print("\n🌐 URL de connexion: http://127.0.0.1:8000/login/")
print("📱 URL interface table: http://127.0.0.1:8000/restaurant/table/")
