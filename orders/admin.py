from django.contrib import admin
from .models import Commande, CommandePlat


class CommandePlatInline(admin.TabularInline):
    model = CommandePlat
    extra = 0
    readonly_fields = ['prix_unitaire']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'serveur', 'etat', 'total', 'date_commande']
    list_filter = ['etat', 'date_commande', 'table']
    search_fields = ['table__numero_table', 'serveur__login']
    list_editable = ['etat']
    inlines = [CommandePlatInline]
    ordering = ['-date_commande']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('table', 'serveur', 'etat', 'total')
        }),
        ('Dates', {
            'fields': ('date_commande', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_commande', 'date_modification']
