from django.contrib import admin
from .models import CategorieDepense, Depense


@admin.register(CategorieDepense)
class CategorieDepenseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation']
    search_fields = ['nom', 'description']
    ordering = ['nom']


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'montant', 'categorie', 'date_depense', 'utilisateur', 'date_creation']
    list_filter = ['categorie', 'date_depense', 'date_creation']
    search_fields = ['description', 'utilisateur__login']
    ordering = ['-date_depense']
    date_hierarchy = 'date_depense'
    
    fieldsets = (
        ('Informations de la dépense', {
            'fields': ('description', 'montant', 'categorie', 'date_depense', 'utilisateur')
        }),
    )
    
    readonly_fields = ['date_creation']
