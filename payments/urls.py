from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.paiement_list, name='paiement_list'),
    path('<int:paiement_id>/', views.paiement_detail, name='paiement_detail'),
    path('<int:paiement_id>/modifier/', views.modifier_paiement, name='modifier_paiement'),
    path('<int:paiement_id>/facture/', views.facture_client, name='facture_client'),
    path('<int:paiement_id>/recu-imprimable/', views.recu_imprimable, name='recu_imprimable'),
    path('nouveau/', views.nouveau_paiement, name='nouveau_paiement'),
    path('caisse/', views.caisse_dashboard, name='caisse_dashboard'),
    path('caisse/ajouter/', views.ajouter_montant_caisse, name='ajouter_montant_caisse'),
    path('caisse/retirer/', views.retirer_montant_caisse, name='retirer_montant_caisse'),
    path('rapport/', views.rapport_paiements, name='rapport_paiements'),
    path('recu/<int:commande_id>/', views.telecharger_recu, name='telecharger_recu'),
]
