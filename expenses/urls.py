from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.depense_list, name='depense_list'),
    path('<int:depense_id>/', views.depense_detail, name='depense_detail'),
    path('nouvelle/', views.nouvelle_depense, name='nouvelle_depense'),
    path('modifier/<int:depense_id>/', views.modifier_depense, name='modifier_depense'),
    path('supprimer/<int:depense_id>/', views.supprimer_depense, name='supprimer_depense'),
    path('statistiques/', views.statistiques_depenses, name='statistiques_depenses'),
    path('rapport/', views.rapport_depenses, name='rapport_depenses'),
]
