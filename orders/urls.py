from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.commande_list, name='commande_list'),
    path('<int:commande_id>/', views.commande_detail, name='commande_detail'),
    path('nouvelle/', views.nouvelle_commande, name='nouvelle_commande'),
    path('changer-etat/<int:commande_id>/', views.changer_etat_commande, name='changer_etat_commande'),
    path('en-cours/', views.commandes_en_cours, name='commandes_en_cours'),
    path('statistiques/', views.statistiques_commandes, name='statistiques_commandes'),
]
