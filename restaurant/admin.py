from django.contrib import admin
from .models import Categorie, TableRestaurant, Plat


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation']
    search_fields = ['nom', 'description']
    ordering = ['nom']


@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    list_display = ['numero_table', 'nombre_places', 'utilisateur', 'est_occupee', 'date_creation']
    list_filter = ['nombre_places', 'est_occupee', 'date_creation']
    search_fields = ['numero_table', 'utilisateur__login']
    ordering = ['numero_table']


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix_unitaire', 'disponible', 'categorie', 'date_creation']
    list_filter = ['disponible', 'categorie', 'date_creation']
    search_fields = ['nom', 'description']
    list_editable = ['disponible']
    ordering = ['nom']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'prix_unitaire', 'image', 'categorie')
        }),
        ('Détails', {
            'fields': ('description', 'disponible')
        }),
    )
