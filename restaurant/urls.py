from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('plat/<int:plat_id>/', views.plat_detail, name='plat_detail'),
    path('table/', views.table_list, name='table_list'),
    path('table/<int:table_id>/', views.table_detail, name='table_detail'),
    path('table/ajouter/', views.nouvelle_table, name='nouvelle_table'),
    path('table/modifier/<int:table_id>/', views.modifier_table, name='modifier_table'),
    path('table/supprimer/<int:table_id>/', views.supprimer_table, name='supprimer_table'),
    path('categorie/', views.categorie_list, name='categorie_list'),
    path('categorie/ajouter/', views.nouvelle_categorie, name='nouvelle_categorie'),
    path('categorie/modifier/<int:categorie_id>/', views.modifier_categorie, name='modifier_categorie'),
    path('categorie/supprimer/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('plat/ajouter/', views.nouveau_plat, name='nouveau_plat'),
    path('plat/modifier/<int:plat_id>/', views.modifier_plat, name='modifier_plat'),
    path('plat/supprimer/<int:plat_id>/', views.supprimer_plat, name='supprimer_plat'),
    
    # Vue pour l'administrateur
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Vues pour les tables (Rtable)
    path('table/home/', views.table_home, name='table_home'),
    path('table/panier/', views.table_panier, name='table_panier'),
    path('table/valider-commande/', views.table_valider_commande, name='table_valider_commande'),
    path('table/commandes/', views.table_commandes, name='table_commandes'),
    
    # Vues pour les serveurs (Rserveur)
    path('serveur/home/', views.serveur_home, name='serveur_home'),
    path('serveur/table/<int:table_id>/', views.serveur_table_commandes, name='serveur_table_commandes'),
    path('serveur/commande/<int:commande_id>/etat/', views.serveur_changer_etat_commande, name='serveur_changer_etat_commande'),
    path('serveur/commande/<int:commande_id>/valider-service/', views.serveur_valider_service, name='serveur_valider_service'),
    path('serveur/table/<int:table_id>/prendre-commande/', views.serveur_prendre_commande, name='serveur_prendre_commande'),
    path('serveur/table/<int:table_id>/creer-commande/', views.serveur_creer_commande, name='serveur_creer_commande'),
    path('serveur/commande/<int:commande_id>/valider-paiement/', views.serveur_valider_paiement, name='serveur_valider_paiement'),
    
    # Vues pour les cuisiniers (Rcuisinier)
    path('cuisinier/home/', views.cuisinier_home, name='cuisinier_home'),
    path('cuisinier/commande/<int:commande_id>/prendre/', views.cuisinier_prendre_commande, name='cuisinier_prendre_commande'),
    path('cuisinier/commande/<int:commande_id>/etat/', views.cuisinier_changer_etat, name='cuisinier_changer_etat'),
    path('cuisinier/commande/<int:commande_id>/prete/', views.cuisinier_marquer_prete, name='cuisinier_marquer_prete'),
    
    # Vues pour les comptables (Rcomptable)
    path('comptable/home/', views.comptable_home, name='comptable_home'),
    path('comptable/commandes/', views.comptable_commandes, name='comptable_commandes'),
    path('comptable/paiements/', views.comptable_paiements, name='comptable_paiements'),
    path('comptable/nouvelle-depense/', views.comptable_nouvelle_depense, name='comptable_nouvelle_depense'),
    
    # API pour l'état des commandes
    path('api/etat-commandes-cuisine/', views.etat_commandes_cuisine, name='etat_commandes_cuisine'),
    
    # Vues pour les QR codes
    path('qr-codes/', views.qr_code_list, name='qr_code_list'),
    path('qr-codes/generer-toutes/', views.generer_qr_codes_toutes, name='generer_qr_codes_toutes'),
    path('qr-codes/regenerer/<int:table_id>/', views.regenerer_qr_code, name='regenerer_qr_code'),
    path('qr-codes/desactiver/<int:table_id>/', views.desactiver_qr_code, name='desactiver_qr_code'),
    path('qr-codes/activer/<int:table_id>/', views.activer_qr_code, name='activer_qr_code'),
    
    # Page mobile accessible via QR code (publique)
    path('qr/<str:code>/', views.qr_menu_mobile, name='qr_menu_mobile'),
    
    # API pour générer les QR codes
    path('api/generer-qr-code/<int:table_id>/', views.api_generer_qr_code, name='api_generer_qr_code'),
    
    # Régénérer tous les QR codes avec nouvelles URLs
    path('qr-codes/regenerer-urls/', views.regenerer_tous_qr_codes_urls, name='regenerer_tous_qr_codes_urls'),
    
    # Imprimer QR code
    path('qr-codes/imprimer/<int:table_id>/', views.imprimer_qr_code, name='imprimer_qr_code'),
    
    # Menu public pour clients (QR Code)
    path('menu-client/<int:table_id>/', views.menu_client_public, name='menu_client_public'),
]
