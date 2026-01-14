from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('categorie/<int:categorie_id>/', views.menu_by_categorie, name='menu_by_categorie'),
    path('plat/<int:plat_id>/', views.plat_detail, name='plat_detail'),
    # Gestion des tables
    path('tables/', views.table_list, name='table_list'),
    path('tables/nouvelle/', views.nouvelle_table, name='nouvelle_table'),
    path('table/<int:table_id>/', views.table_detail, name='table_detail'),
    path('toggle-plat/<int:plat_id>/', views.toggle_plat_disponibilite, name='toggle_plat_disponibilite'),
    
    # Gestion des plats (cuisinier/admin)
    path('nouveau-plat/', views.nouveau_plat, name='nouveau_plat'),
    path('modifier-plat/<int:plat_id>/', views.modifier_plat, name='modifier_plat'),
    path('supprimer-plat/<int:plat_id>/', views.supprimer_plat, name='supprimer_plat'),
    
    # Gestion des catégories (cuisinier/admin)
    path('categories/', views.liste_categories, name='liste_categories'),
    path('nouvelle-categorie/', views.nouvelle_categorie, name='nouvelle_categorie'),
    
    # API pour les suggestions
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # API pour l'état des commandes en cuisine
    path('api/etat-commandes-cuisine/', views.etat_commandes_cuisine, name='etat_commandes_cuisine'),
    
    # Interface pour les tables (Rtable)
    path('table/', views.table_home, name='table_home'),
    path('table/panier/', views.table_panier, name='table_panier'),
    path('table/valider-commande/', views.table_valider_commande, name='table_valider_commande'),
    path('table/commandes/', views.table_commandes, name='table_commandes'),
    
    # URLs pour les serveurs (Rserveur)
    path('serveur/', views.serveur_home, name='serveur_home'),
    path('serveur/table/<int:table_id>/commandes/', views.serveur_table_commandes, name='serveur_table_commandes'),
    path('serveur/commande/<int:commande_id>/valider-service/', views.serveur_valider_service, name='serveur_valider_service'),
    path('serveur/commande/<int:commande_id>/valider-paiement/', views.serveur_valider_paiement, name='serveur_valider_paiement'),
    
    # URLs pour les cuisiniers (Rcuisinier)
    path('cuisinier/', views.cuisinier_home, name='cuisinier_home'),
    path('cuisinier/commande/<int:commande_id>/prendre/', views.cuisinier_prendre_commande, name='cuisinier_prendre_commande'),
    path('cuisinier/commande/<int:commande_id>/changer-etat/', views.cuisinier_changer_etat, name='cuisinier_changer_etat'),
    path('cuisinier/commande/<int:commande_id>/marquer-prete/', views.cuisinier_marquer_prete, name='cuisinier_marquer_prete'),
    
    # URLs pour les comptables (Rcomptable)
    path('comptable/', views.comptable_home, name='comptable_home'),
    path('comptable/commandes/', views.comptable_commandes, name='comptable_commandes'),
    path('comptable/paiements/', views.comptable_paiements, name='comptable_paiements'),
    path('comptable/nouvelle-depense/', views.comptable_nouvelle_depense, name='comptable_nouvelle_depense'),
]
