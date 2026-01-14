from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.paiement_list, name='paiement_list'),
    path('<int:paiement_id>/', views.paiement_detail, name='paiement_detail'),
    path('nouveau/', views.nouveau_paiement, name='nouveau_paiement'),
    path('caisse/', views.caisse_dashboard, name='caisse_dashboard'),
    path('caisse/ajouter/', views.ajouter_montant_caisse, name='ajouter_montant_caisse'),
    path('caisse/retirer/', views.retirer_montant_caisse, name='retirer_montant_caisse'),
    path('rapport/', views.rapport_paiements, name='rapport_paiements'),
]
