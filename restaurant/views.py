from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from accounts.decorators import (admin_or_role_required, admin_or_restaurant_staff_required, admin_or_table_required,
                                  admin_or_serveur_required, admin_or_cuisinier_required, admin_or_caissier_required,
                                  admin_or_comptable_required, admin_or_financial_required)
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from .models import Plat, TableRestaurant, Categorie, QRCode
from .forms import PlatForm, CategorieForm
from orders.models import Commande, EtatCommande
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json

def menu_list(request):
    """Liste des plats du menu avec filtres et suggestions AJAX"""
    # Vérifier si c'est une demande de suggestions AJAX
    if request.GET.get('suggestions') == '1':
        search_query = request.GET.get('search', '')
        suggestions = []
        
        if search_query and len(search_query) >= 2:
            plats = Plat.objects.filter(
                models.Q(nom__icontains=search_query) |
                models.Q(description__icontains=search_query)
            ).filter(disponible=True)[:5]  # Limiter à 5 suggestions
            
            suggestions = [
                {
                    'id': plat.id,
                    'name': plat.nom,
                    'price': str(plat.prix_unitaire),
                    'type': plat.get_type_plat_display() if plat.type_plat else '',
                    'category': plat.categorie.nom if plat.categorie else ''
                }
                for plat in plats
            ]
        
        return JsonResponse({'suggestions': suggestions})
    
    # Récupérer les paramètres de filtre
    search_query = request.GET.get('search', '')
    type_plat_filter = request.GET.get('type_plat', '')
    categorie_filter = request.GET.get('categorie', '')
    
    # Filtrer les plats (inclure les indisponibles pour voir tous les plats)
    plats = Plat.objects.all()
    
    # Appliquer les filtres
    if search_query:
        plats = plats.filter(
            models.Q(nom__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    if type_plat_filter:
        plats = plats.filter(type_plat=type_plat_filter)
    
    if categorie_filter:
        plats = plats.filter(categorie__id=categorie_filter)
    
    categories = Categorie.objects.all()
    type_plat_choices = Plat.TYPE_PLAT_CHOICES
    
    context = {
        'plats': plats,
        'categories': categories,
        'type_plat_choices': type_plat_choices,
        'search_query': search_query,
        'type_plat_filter': type_plat_filter,
        'categorie_filter': categorie_filter,
    }
    return render(request, 'restaurant/menu_list.html', context)

@login_required
def plat_detail(request, plat_id):
    """Détail d'un plat"""
    plat = get_object_or_404(Plat, id=plat_id)
    return render(request, 'restaurant/plat_detail.html', {'plat': plat})

@login_required
def table_list(request):
    """Liste des tables du restaurant"""
    tables = TableRestaurant.objects.all()
    return render(request, 'restaurant/table_list.html', {'tables': tables})

@login_required
def nouvelle_table(request):
    """Créer une nouvelle table (admin seulement)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès non autorisé. Réservé aux administrateurs.")
        return redirect('restaurant:table_list')
    
    if request.method == 'POST':
        numero_table = request.POST.get('numero_table')
        nombre_places = request.POST.get('nombre_places')
        utilisateur_id = request.POST.get('utilisateur')
        
        # Validation
        if not numero_table or not nombre_places:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('restaurant:nouvelle_table')
        
        # Vérifier si le numéro de table existe déjà
        if TableRestaurant.objects.filter(numero_table=numero_table).exists():
            messages.error(request, f"La table numéro {numero_table} existe déjà.")
            return redirect('restaurant:nouvelle_table')
        
        try:
            # Créer la table
            table = TableRestaurant.objects.create(
                numero_table=int(numero_table),
                nombre_places=int(nombre_places),
                utilisateur_id=utilisateur_id if utilisateur_id else None,
                est_occupee=False
            )
            
            messages.success(request, f"Table {table.numero_table} créée avec succès!")
            return redirect('restaurant:table_list')
            
        except ValueError:
            messages.error(request, "Veuillez entrer des valeurs numériques valides.")
            return redirect('restaurant:nouvelle_table')
    
    # Récupérer les utilisateurs pour le formulaire
    utilisateurs = User.objects.all()
    return render(request, 'restaurant/nouvelle_table.html', {'utilisateurs': utilisateurs})

@login_required
def modifier_table(request, table_id):
    """Modifier une table (réservé à l'admin)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('restaurant:table_list')
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if request.method == 'POST':
        numero_table = request.POST.get('numero_table')
        nombre_places = request.POST.get('nombre_places')
        
        if not numero_table or not nombre_places:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('restaurant:modifier_table', table_id=table_id)
        
        try:
            nombre_places = int(nombre_places)
            if nombre_places <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, "Le nombre de places doit être un nombre positif.")
            return redirect('restaurant:modifier_table', table_id=table_id)
        
        # Vérifier si le numéro de table est déjà utilisé (par une autre table)
        if TableRestaurant.objects.filter(numero_table=numero_table).exclude(id=table_id).exists():
            messages.error(request, "Ce numéro de table est déjà utilisé.")
            return redirect('restaurant:modifier_table', table_id=table_id)
        
        table.numero_table = int(numero_table)
        table.nombre_places = nombre_places
        table.save()
        
        messages.success(request, f"Table {numero_table} modifiée avec succès!")
        return redirect('restaurant:table_list')
    
    context = {
        'table': table,
        'utilisateurs': User.objects.all()
    }
    return render(request, 'restaurant/modifier_table.html', context)

@login_required
def supprimer_table(request, table_id):
    """Supprimer une table (réservé à l'admin)"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('restaurant:table_list')
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if request.method == 'POST':
        numero_table = table.numero_table
        table.delete()
        messages.success(request, f"Table {numero_table} supprimée avec succès!")
        return redirect('restaurant:table_list')
    
    context = {
        'table': table
    }
    return render(request, 'restaurant/supprimer_table.html', context)

@login_required
def table_detail(request, table_id):
    """Détail d'une table"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    return render(request, 'restaurant/table_detail.html', {'table': table})

@require_POST
@login_required
def toggle_plat_disponibilite(request, plat_id):
    """Basculer la disponibilité d'un plat"""
    plat = get_object_or_404(Plat, id=plat_id)
    plat.disponible = not plat.disponible
    plat.save()
    return JsonResponse({
        'success': True,
        'disponible': plat.disponible
    })

def menu_by_categorie(request, categorie_id):
    """Menu filtré par catégorie"""
    categorie = get_object_or_404(Categorie, id=categorie_id)
    plats = Plat.objects.filter(categorie=categorie, disponible=True)
    context = {
        'categorie': categorie,
        'plats': plats
    }
    return render(request, 'restaurant/menu_by_categorie.html', context)


@login_required
def nouveau_plat(request):
    """Créer un nouveau plat (réservé au cuisinier et admin)"""
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.error(request, "Vous n'avez pas les permissions pour créer un plat.")
        return redirect('restaurant:menu_list')
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            plat = form.save()
            messages.success(request, f'Le plat "{plat.nom}" a été créé avec succès!')
            return redirect('restaurant:plat_detail', plat_id=plat.id)
    else:
        form = PlatForm()
    
    context = {
        'form': form,
        'title': 'Nouveau Plat'
    }
    return render(request, 'restaurant/nouveau_plat.html', context)


@login_required
def modifier_plat(request, plat_id):
    """Modifier un plat (réservé au cuisinier et admin)"""
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.error(request, "Vous n'avez pas les permissions pour modifier un plat.")
        return redirect('restaurant:menu_list')
    
    plat = get_object_or_404(Plat, id=plat_id)
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            plat = form.save()
            messages.success(request, f'Le plat "{plat.nom}" a été modifié avec succès!')
            return redirect('restaurant:plat_detail', plat_id=plat.id)
    else:
        form = PlatForm(instance=plat)
    
    context = {
        'form': form,
        'plat': plat,
        'title': 'Modifier un Plat'
    }
    return render(request, 'restaurant/modifier_plat.html', context)


@login_required
def supprimer_plat(request, plat_id):
    """Supprimer un plat (réservé à l'admin)"""
    if not request.user.is_admin():
        messages.error(request, "Seul l'administrateur peut supprimer un plat.")
        return redirect('restaurant:menu_list')
    
    plat = get_object_or_404(Plat, id=plat_id)
    
    if request.method == 'POST':
        nom_plat = plat.nom
        plat.delete()
        messages.success(request, f'Le plat "{nom_plat}" a été supprimé avec succès!')
        return redirect('restaurant:menu_list')
    
    context = {
        'plat': plat
    }
    return render(request, 'restaurant/supprimer_plat.html', context)


@login_required
def categorie_list(request):
    """Liste des catégories (réservé au cuisinier et admin)"""
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.error(request, "Vous n'avez pas les permissions pour gérer les catégories.")
        return redirect('restaurant:menu_list')
    
    categories = Categorie.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'restaurant/categorie_list.html', context)


@login_required
def nouvelle_categorie(request):
    """Créer une nouvelle catégorie (réservé au cuisinier et admin)"""
    # Temporairement enlevé la vérification de permissions pour tester
    # if not (request.user.is_cuisinier() or request.user.is_admin()):
    #     messages.error(request, "Vous n'avez pas les permissions pour créer une catégorie.")
    #     return redirect('restaurant:menu_list')
    
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            categorie = form.save()
            messages.success(request, f'La catégorie "{categorie.nom}" a été créée avec succès!')
            return redirect('restaurant:liste_categories')
    else:
        form = CategorieForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle Catégorie'
    }
    return render(request, 'restaurant/nouvelle_categorie.html', context)


@login_required
def modifier_categorie(request, categorie_id):
    """Modifier une catégorie (réservé au cuisinier et admin)"""
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.error(request, "Vous n'avez pas les permissions pour modifier une catégorie.")
        return redirect('restaurant:menu_list')
    
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            categorie = form.save()
            messages.success(request, f'La catégorie "{categorie.nom}" a été modifiée avec succès!')
            return redirect('restaurant:categorie_list')
    else:
        form = CategorieForm(instance=categorie)
    
    context = {
        'form': form,
        'categorie': categorie,
        'title': 'Modifier une Catégorie'
    }
    return render(request, 'restaurant/modifier_categorie.html', context)


@login_required
def supprimer_categorie(request, categorie_id):
    """Supprimer une catégorie (réservé à l'admin)"""
    if not request.user.is_admin():
        messages.error(request, "Seul l'administrateur peut supprimer une catégorie.")
        return redirect('restaurant:menu_list')
    
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    # Vérifier s'il y a des plats associés
    if categorie.plat_set.exists():
        messages.error(request, f"Impossible de supprimer la catégorie '{categorie.nom}' car elle contient des plats.")
        return redirect('restaurant:categorie_list')
    
    if request.method == 'POST':
        nom_categorie = categorie.nom
        categorie.delete()
        messages.success(request, f'La catégorie "{nom_categorie}" a été supprimée avec succès!')
        return redirect('restaurant:categorie_list')
    
    context = {
        'categorie': categorie
    }
    return render(request, 'restaurant/supprimer_categorie.html', context)


@csrf_exempt
def search_suggestions(request):
    """API pour les suggestions de recherche de plats"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Rechercher des plats correspondants
    plats = Plat.objects.filter(
        models.Q(nom__icontains=query) | 
        models.Q(description__icontains=query)
    ).filter(disponible=True)[:10]  # Limiter à 10 suggestions
    
    suggestions = []
    for plat in plats:
        suggestions.append({
            'id': plat.id,
            'nom': plat.nom,
            'type_plat': plat.get_type_plat_display(),
            'prix': str(plat.prix_unitaire),
            'image': plat.image.url if plat.image else None,
            'url': f"/restaurant/plat/{plat.id}/"
        })
    
    return JsonResponse({'suggestions': suggestions})


# Vues pour les tables (Rtable)
def table_home(request):
    """Page d'accueil pour les tables (publique et admin)"""
    
    # Récupérer la table - soit depuis l'utilisateur connecté, soit depuis la session/paramètre
    table = None
    
    if request.user.is_authenticated:
        if request.user.role == 'Radmin':
            # Pour l'admin, afficher la première table ou permettre de choisir
            tables = TableRestaurant.objects.all()
            if not tables.exists():
                messages.error(request, "Aucune table disponible.")
                return redirect('restaurant:table_list')
            # Pour l'instant, on prend la première table
            table = tables.first()
            messages.info(request, f"Vue en tant qu'administrateur - Table {table.numero_table}")
        elif hasattr(request.user, 'table'):
            try:
                table = request.user.table
            except TableRestaurant.DoesNotExist:
                messages.error(request, "Aucune table associée à votre compte.")
                return redirect('accounts:login')
        else:
            # Utilisateur connecté mais sans table, prendre la première table disponible
            table = TableRestaurant.objects.first()
            if table:
                messages.info(request, f"Table {table.numero_table} sélectionnée")
    else:
        # Client non connecté - prendre la première table disponible
        table = TableRestaurant.objects.first()
        if not table:
            return render(request, 'restaurant/qr_code_erreur.html', {'erreur': 'Aucune table disponible'})
    
    # Récupérer les plats disponibles
    plats = Plat.objects.filter(disponible=True).order_by('nom')
    categories = Categorie.objects.all()
    
    context = {
        'table': table,
        'plats': plats,
        'categories': categories,
        'is_client': not request.user.is_authenticated  # Indicateur pour le template
    }
    return render(request, 'restaurant/table_home.html', context)


def table_panier(request):
    """Gestion du panier pour les tables (et admin)"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter':
            plat_id = request.POST.get('plat_id')
            quantite = int(request.POST.get('quantite', 1))
            
            # Validation de la quantité (1-10)
            if quantite < 1 or quantite > 10:
                return JsonResponse({'error': 'La quantité doit être entre 1 et 10'}, status=400)
            
            plat = get_object_or_404(Plat, id=plat_id, disponible=True)
            
            # Récupérer ou créer le panier en session
            panier = request.session.get('panier', {})
            
            if plat_id in panier:
                # Vérifier que la quantité totale ne dépasse pas 10
                nouvelle_quantite = panier[plat_id]['quantite'] + quantite
                if nouvelle_quantite > 10:
                    return JsonResponse({'error': 'La quantité maximale est de 10'}, status=400)
                panier[plat_id]['quantite'] = nouvelle_quantite
            else:
                panier[plat_id] = {
                    'nom': plat.nom,
                    'prix': float(plat.prix_unitaire),
                    'quantite': quantite,
                    'image': plat.image.url if plat.image else None
                }
            
            request.session['panier'] = panier
            return JsonResponse({'success': True, 'panier': panier})
        
        elif action == 'modifier':
            plat_id = request.POST.get('plat_id')
            quantite = int(request.POST.get('quantite', 1))
            
            if quantite < 1 or quantite > 10:
                return JsonResponse({'error': 'La quantité doit être entre 1 et 10'}, status=400)
            
            panier = request.session.get('panier', {})
            
            if plat_id in panier:
                panier[plat_id]['quantite'] = quantite
                request.session['panier'] = panier
                return JsonResponse({'success': True, 'panier': panier})
            else:
                return JsonResponse({'error': 'Plat non trouvé dans le panier'}, status=404)
        
        elif action == 'supprimer':
            plat_id = request.POST.get('plat_id')
            
            panier = request.session.get('panier', {})
            
            if plat_id in panier:
                del panier[plat_id]
                request.session['panier'] = panier
                return JsonResponse({'success': True, 'panier': panier})
            else:
                return JsonResponse({'error': 'Plat non trouvé dans le panier'}, status=404)
        
        elif action == 'vider':
            request.session['panier'] = {}
            return JsonResponse({'success': True, 'panier': {}})
    
    # GET - Récupérer le panier actuel
    panier = request.session.get('panier', {})
    return JsonResponse({'panier': panier})


def table_valider_commande(request):
    """Validation du panier et création de commande (et admin)"""
    
    panier = request.session.get('panier', {})
    
    if not panier:
        messages.error(request, "Votre panier est vide.")
        return redirect('restaurant:table_home')
    
    # Récupérer la table
    if request.user.is_authenticated and request.user.role == 'Radmin':
        # Pour l'admin, utiliser la première table
        table = TableRestaurant.objects.first()
        if not table:
            messages.error(request, "Aucune table disponible.")
            return redirect('restaurant:table_list')
    elif request.user.is_authenticated and hasattr(request.user, 'table'):
        try:
            table = request.user.table
        except TableRestaurant.DoesNotExist:
            messages.error(request, "Aucune table associée à votre compte.")
            return redirect('accounts:login')
    else:
        # Client non connecté - utiliser la première table disponible
        table = TableRestaurant.objects.first()
        if not table:
            messages.error(request, "Aucune table disponible.")
            return redirect('restaurant:table_home')
    
    if request.method == 'POST':
        from orders.models import Commande, CommandePlat, EtatCommande
        
        # Créer la commande
        commande = Commande.objects.create(
            table=table,
            serveur=None,  # Pas de serveur pour une commande de table
            etat=EtatCommande.EN_ATTENTE,
            total=0
        )
        
        # Ajouter les plats à la commande
        total = 0
        for plat_id, item in panier.items():
            plat = get_object_or_404(Plat, id=plat_id)
            quantite = item['quantite']
            
            CommandePlat.objects.create(
                commande=commande,
                plat=plat,
                quantite=quantite,
                prix_unitaire=plat.prix_unitaire
            )
            
            total += plat.prix_unitaire * quantite
        
        # Mettre à jour le total
        commande.total = total
        commande.save()
        
        # Vider le panier
        request.session['panier'] = {}
        
        messages.success(request, f"Commande #{commande.id} créée avec succès!")
        return redirect('restaurant:table_commandes')
    
    # Afficher le récapitulatif
    # Calculer le total pour le template
    total = 0
    for plat_id, item in panier.items():
        total += item['prix'] * item['quantite']
    
    context = {
        'panier': panier,
        'table': table,
        'total': total
    }
    return render(request, 'restaurant/table_valider_commande.html', context)


@admin_or_serveur_required
def serveur_home(request):
    """Page d'accueil pour les serveurs (et admin)"""
    
    # Récupérer toutes les tables avec leur état
    tables = TableRestaurant.objects.all().order_by('numero_table')
    
    # Déterminer l'état de chaque table
    tables_data = []
    for table in tables:
        # Chercher la dernière commande pour cette table
        derniere_commande = Commande.objects.filter(table=table).order_by('-date_commande').first()
        
        etat_table = 'Libre'
        etat_couleur = 'green'
        
        if derniere_commande:
            if derniere_commande.etat == EtatCommande.EN_ATTENTE:
                etat_table = 'Commande en attente'
                etat_couleur = 'yellow'
            elif derniere_commande.etat == EtatCommande.EN_PREPARATION:
                etat_table = 'Commande en préparation'
                etat_couleur = 'orange'
            elif derniere_commande.etat == EtatCommande.EN_COURS:
                etat_table = 'Commande en cours'
                etat_couleur = 'blue'
            elif derniere_commande.etat == EtatCommande.TERMINEE:
                # Vérifier si la commande est payée
                from payments.models import Paiement
                paiement = Paiement.objects.filter(commande=derniere_commande).first()
                if paiement:
                    etat_table = 'Commande payée'
                    etat_couleur = 'green'
                else:
                    etat_table = 'Commande servie'
                    etat_couleur = 'purple'
        
        tables_data.append({
            'table': table,
            'etat': etat_table,
            'etat_couleur': etat_couleur,
            'derniere_commande': derniere_commande
        })
    
    context = {
        'tables_data': tables_data
    }
    return render(request, 'restaurant/serveur_home.html', context)


@admin_or_serveur_required
def serveur_table_commandes(request, table_id):
    """Consultation des commandes d'une table spécifique (et admin)"""
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    commandes = Commande.objects.filter(table=table).select_related('paiement').order_by('-date_commande')
    
    context = {
        'table': table,
        'commandes': commandes
    }
    return render(request, 'restaurant/serveur_table_commandes.html', context)


@admin_or_serveur_required
def serveur_changer_etat_commande(request, commande_id):
    """Interface pour changer l'état d'une commande (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        nouvel_etat = request.POST.get('nouvel_etat')
        
        # Valider la transition d'état
        etats_autorises = {
            'EN_ATTENTE': ['EN_PREPARATION', 'ANNULEE'],
            'EN_PREPARATION': ['EN_COURS', 'ANNULEE'],
            'EN_COURS': ['TERMINEE', 'ANNULEE'],
            'TERMINEE': [],  # État final
            'ANNULEE': []    # État final
        }
        
        if nouvel_etat in etats_autorises.get(commande.etat, []):
            ancien_etat = commande.get_etat_display()
            commande.etat = nouvel_etat
            commande.save()
            
            messages.success(request, f"Commande #{commande.id} : {ancien_etat} → {commande.get_etat_display()}")
            
            # Si la commande est terminée, proposer le paiement
            if nouvel_etat == 'TERMINEE' and not commande.paiement_set.exists():
                messages.info(request, "La commande est prête. Vous pouvez maintenant enregistrer le paiement.")
        else:
            messages.error(request, "Transition d'état non autorisée.")
        
        return redirect('restaurant:serveur_table_commandes', table_id=commande.table.id)
    
    # Déterminer les états possibles depuis l'état actuel
    etats_possibles = []
    if commande.etat == 'EN_ATTENTE':
        etats_possibles = [
            ('EN_PREPARATION', 'Prise en charge'),
            ('ANNULEE', 'Annuler')
        ]
    elif commande.etat == 'EN_PREPARATION':
        etats_possibles = [
            ('EN_COURS', 'En cours de service'),
            ('ANNULEE', 'Annuler')
        ]
    elif commande.etat == 'EN_COURS':
        etats_possibles = [
            ('TERMINEE', 'Servie'),
            ('ANNULEE', 'Annuler')
        ]
    
    context = {
        'commande': commande,
        'etats_possibles': etats_possibles,
    }
    return render(request, 'restaurant/serveur_changer_etat_commande.html', context)


@admin_or_serveur_required
def serveur_valider_service(request, commande_id):
    """Validation du service (plats servis) - conservé pour compatibilité (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        commande.etat = EtatCommande.TERMINEE
        commande.save()
        messages.success(request, f"Commande #{commande.id} marquée comme servie.")
        return redirect('restaurant:serveur_table_commandes', table_id=commande.table.id)
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/serveur_valider_service.html', context)


@admin_or_cuisinier_required
def cuisinier_home(request):
    """Page d'accueil pour les cuisiniers (et admin)"""
    
    # Récupérer les commandes en attente et en préparation
    commandes_en_attente = Commande.objects.filter(etat=EtatCommande.EN_ATTENTE).order_by('date_commande')
    commandes_en_preparation = Commande.objects.filter(
        etat__in=[EtatCommande.EN_PREPARATION, EtatCommande.EN_COURS]
    ).order_by('date_commande')
    
    context = {
        'commandes_en_attente': commandes_en_attente,
        'commandes_en_preparation': commandes_en_preparation,
    }
    return render(request, 'restaurant/cuisinier_home.html', context)


@admin_or_cuisinier_required
def cuisinier_prendre_commande(request, commande_id):
    """Prendre une commande en charge (EN_ATTENTE → EN_PREPARATION) (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if commande.etat != EtatCommande.EN_ATTENTE:
        messages.error(request, "Cette commande n'est plus en attente.")
        return redirect('restaurant:cuisinier_home')
    
    if request.method == 'POST':
        commande.etat = EtatCommande.EN_PREPARATION
        commande.save()
        messages.success(request, f"Commande #{commande.id} prise en charge.")
        return redirect('restaurant:cuisinier_home')
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/cuisinier_prendre_commande.html', context)


@admin_or_cuisinier_required
def cuisinier_changer_etat(request, commande_id):
    """Changer l'état d'une commande (EN_PREPARATION ↔ EN_COURS) (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if commande.etat not in [EtatCommande.EN_PREPARATION, EtatCommande.EN_COURS]:
        messages.error(request, "Cette commande n'est pas en préparation.")
        return redirect('restaurant:cuisinier_home')
    
    if request.method == 'POST':
        nouvel_etat = request.POST.get('nouvel_etat')
        if nouvel_etat in ['EN_PREPARATION', 'EN_COURS']:
            commande.etat = nouvel_etat
            commande.save()
            
            etat_texte = "en préparation" if nouvel_etat == 'EN_PREPARATION' else "en cours de cuisson"
            messages.success(request, f"Commande #{commande.id} marquée comme {etat_texte}.")
        
        return redirect('restaurant:cuisinier_home')
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/cuisinier_changer_etat.html', context)


@admin_or_cuisinier_required
def cuisinier_marquer_prete(request, commande_id):
    """Marquer une commande comme prête pour livraison (EN_COURS → TERMINEE) (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if commande.etat != EtatCommande.EN_COURS:
        messages.error(request, "Cette commande doit être en cours pour être marquée comme prête.")
        return redirect('restaurant:cuisinier_home')
    
    if request.method == 'POST':
        commande.etat = EtatCommande.TERMINEE
        commande.save()
        messages.success(request, f"Commande #{commande.id} marquée comme prête pour livraison.")
        return redirect('restaurant:cuisinier_home')
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/cuisinier_marquer_prete.html', context)


@admin_or_comptable_required
def comptable_home(request):
    """Page d'accueil pour les comptables (et admin)"""
    
    # Calculer le solde de la caisse
    from payments.models import Paiement
    from expenses.models import Depense
    
    # Total des paiements (entrées)
    total_entrées = Paiement.objects.aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Total des dépenses (sorties)
    total_sorties = Depense.objects.aggregate(
        total=models.Sum('montant')
    )['total'] or 0
    
    # Solde actuel
    solde_caisse = total_entrées - total_sorties
    
    # Récupérer les commandes et paiements récents
    commandes_recentes = Commande.objects.order_by('-date_commande')[:10]
    paiements_recents = Paiement.objects.order_by('-date_paiement')[:10]
    depenses_recentes = Depense.objects.order_by('-date_depense')[:10]
    
    context = {
        'solde_caisse': solde_caisse,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
        'commandes_recentes': commandes_recentes,
        'paiements_recents': paiements_recents,
        'depenses_recentes': depenses_recentes,
    }
    return render(request, 'restaurant/comptable_home.html', context)


@admin_or_role_required('Rcomptable', 'Rserveur')
def comptable_commandes(request):
    """Consultation de la liste des commandes (et admin)"""
    
    commandes = Commande.objects.all().order_by('-date_commande')
    
    context = {
        'commandes': commandes
    }
    return render(request, 'restaurant/comptable_commandes.html', context)


@admin_or_comptable_required
def comptable_paiements(request):
    """Consultation des paiements (et admin)"""
    
    from payments.models import Paiement
    paiements = Paiement.objects.all().order_by('-date_paiement')
    
    context = {
        'paiements': paiements
    }
    return render(request, 'restaurant/comptable_paiements.html', context)


@admin_or_comptable_required
def comptable_nouvelle_depense(request):
    """Enregistrement d'une nouvelle dépense (et admin)"""
    
    if request.method == 'POST':
        from expenses.models import Depense
        from payments.models import Paiement
        
        # Vérifier le solde de la caisse
        total_entrées = Paiement.objects.aggregate(
            total=models.Sum('montant')
        )['total'] or 0
        
        total_sorties = Depense.objects.aggregate(
            total=models.Sum('montant')
        )['total'] or 0
        
        solde_caisse = total_entrées - total_sorties
        montant_depense = float(request.POST.get('montant'))
        
        if montant_depense > solde_caisse:
            messages.error(request, f"Solde de caisse insuffisant. Solde actuel: {solde_caisse} GNF")
            return redirect('restaurant:comptable_nouvelle_depense')
        
        # Créer la dépense
        depense = Depense.objects.create(
            description=request.POST.get('motif'),
            montant=montant_depense,
            date_depense=request.POST.get('date_depense'),
            utilisateur=request.user
        )
        
        messages.success(request, f"Dépense de {montant_depense} GNF enregistrée avec succès.")
        return redirect('restaurant:comptable_home')
    
    context = {}
    return render(request, 'restaurant/comptable_nouvelle_depense.html', context)


@admin_or_serveur_required
def serveur_prendre_commande(request, table_id):
    """Interface pour que le serveur prenne une commande directement (et admin)"""
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    # Récupérer tous les plats disponibles
    plats = Plat.objects.filter(disponible=True)
    
    # Séparer les plats qui nécessitent une préparation et ceux qui sont servis directement
    plats_a_preparer = plats.filter(necessite_preparation=True)
    plats_service_direct = plats.filter(necessite_preparation=False)
    
    context = {
        'table': table,
        'plats_a_preparer': plats_a_preparer,
        'plats_service_direct': plats_service_direct,
    }
    return render(request, 'restaurant/serveur_prendre_commande.html', context)


@admin_or_serveur_required
def serveur_creer_commande(request, table_id):
    """Créer une commande depuis l'interface serveur (et admin)"""
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if request.method == 'POST':
        plat_ids = request.POST.getlist('plats')
        quantites = request.POST.getlist('quantites')
        
        if not plat_ids:
            messages.error(request, "Veuillez sélectionner au moins un plat.")
            return redirect('restaurant:serveur_prendre_commande', table_id=table_id)
        
        # Créer la commande
        commande = Commande.objects.create(
            table=table,
            serveur=request.user,
            etat=EtatCommande.EN_ATTENTE
        )
        
        # Ajouter les plats à la commande
        total = 0
        plats_a_preparer = False
        plats_service_direct = False
        
        for i, plat_id in enumerate(plat_ids):
            try:
                plat = Plat.objects.get(id=plat_id)
                quantite = int(quantites[i])
                
                if quantite > 0:
                    CommandePlat.objects.create(
                        commande=commande,
                        plat=plat,
                        quantite=quantite,
                        prix_unitaire=plat.prix_unitaire
                    )
                    total += plat.prix_unitaire * quantite
                    
                    # Vérifier le type de service nécessaire
                    if plat.necessite_preparation:
                        plats_a_preparer = True
                    else:
                        plats_service_direct = True
                        
            except (Plat.DoesNotExist, ValueError, IndexError):
                continue
        
        commande.calculer_total()
        
        # Déterminer l'état initial de la commande
        if plats_a_preparer and plats_service_direct:
            # Commande mixte : certains plats en cuisine, d'autres service direct
            commande.etat = EtatCommande.EN_ATTENTE
            messages.info(request, f"Commande #{commande.id} créée. Les plats nécessitant une préparation sont envoyés en cuisine.")
        elif plats_service_direct and not plats_a_preparer:
            # Uniquement des plats service direct : marquer comme prête à servir
            commande.etat = EtatCommande.TERMINEE
            messages.success(request, f"Commande #{commande.id} créée et prête à être servie immédiatement.")
        else:
            # Uniquement des plats à préparer
            commande.etat = EtatCommande.EN_ATTENTE
            messages.success(request, f"Commande #{commande.id} créée et envoyée en cuisine.")
        
        commande.save()
        
        return redirect('restaurant:serveur_table_commandes', table_id=table_id)
    
    return redirect('restaurant:serveur_prendre_commande', table_id=table_id)


@admin_or_serveur_required
def serveur_valider_paiement(request, commande_id):
    """Validation du paiement (et admin)"""
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        # Créer le paiement
        from payments.models import Paiement
        paiement = Paiement.objects.create(
            commande=commande,
            montant=commande.total,
            methode='ESPECES',  # Par défaut, peut être modifié
            utilisateur=request.user,
            statut='PAYE'
        )
        
        messages.success(request, f"Paiement de {commande.total} GNF validé avec succès.")
        
        # Rediriger vers la page des commandes de la table pour voir l'état mis à jour
        return redirect('restaurant:serveur_table_commandes', table_id=commande.table.id)
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/serveur_valider_paiement.html', context)


@admin_or_table_required
def table_commandes(request):
    """Liste des commandes de la table (et admin)"""
    
    if request.user.role == 'Radmin':
        # Pour l'admin, utiliser la première table
        table = TableRestaurant.objects.first()
        if not table:
            messages.error(request, "Aucune table disponible.")
            return redirect('restaurant:table_list')
    else:
        try:
            table = request.user.table
        except TableRestaurant.DoesNotExist:
            messages.error(request, "Aucune table associée à votre compte.")
            return redirect('accounts:login')
    
    # Récupérer uniquement les commandes de cette table
    from orders.models import Commande
    commandes = Commande.objects.filter(table=table).order_by('-date_commande')
    
    context = {
        'table': table,
        'commandes': commandes
    }
    return render(request, 'restaurant/table_commandes.html', context)


@csrf_exempt
def etat_commandes_cuisine(request):
    """API pour obtenir l'état des commandes en cuisine"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Récupérer les commandes actives (non terminées)
        commandes = Commande.objects.exclude(etat=EtatCommande.TERMINEE).order_by('-date_commande')
        
        # Si l'utilisateur est une table, filtrer seulement ses commandes
        if request.user.role == 'Rtable':
            try:
                table = request.user.table
                commandes = commandes.filter(table=table)
            except TableRestaurant.DoesNotExist:
                commandes = Commande.objects.none()
        
        commandes_data = []
        for commande in commandes:
            # Calculer le temps estimé
            temps_estime = None
            if commande.etat in [EtatCommande.EN_ATTENTE, EtatCommande.EN_PREPARATION]:
                temps_estime = 15  # 15 minutes par défaut
            
            # Récupérer les plats
            plats_data = []
            for cp in commande.commandeplat_set.all():
                plats_data.append({
                    'nom': cp.plat.nom,
                    'quantite': cp.quantite,
                    'prix_unitaire': str(cp.prix_unitaire),
                    'sous_total': str(cp.sous_total()),
                    'necessite_preparation': cp.plat.necessite_preparation
                })
            
            commandes_data.append({
                'id': commande.id,
                'table_numero': commande.table.numero_table,
                'etat': commande.etat,
                'etat_display': commande.get_etat_display(),
                'heure': commande.date_commande.strftime('%H:%M'),
                'total': str(commande.total),
                'plats': plats_data,
                'temps_estime': temps_estime,
                'date_modification': commande.date_modification.strftime('%H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'commandes': commandes_data,
            'total': len(commandes_data),
            'user_role': request.user.role,
            'table_numero': getattr(request.user.table, 'numero_table', None) if request.user.role == 'Rtable' else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def admin_dashboard(request):
    """Tableau de bord administrateur avec accès à tout"""
    if request.user.role != 'Radmin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accounts:login')
    
    # Statistiques générales
    from orders.models import Commande, EtatCommande
    from payments.models import Paiement
    from expenses.models import Depense
    from accounts.models import User
    
    # Statistiques des commandes
    total_commandes = Commande.objects.count()
    commandes_aujourdhui = Commande.objects.filter(date_commande__date=timezone.now().date()).count()
    
    commandes_par_etat = {
        'EN_ATTENTE': Commande.objects.filter(etat=EtatCommande.EN_ATTENTE).count(),
        'EN_PREPARATION': Commande.objects.filter(etat=EtatCommande.EN_PREPARATION).count(),
        'EN_COURS': Commande.objects.filter(etat=EtatCommande.EN_COURS).count(),
        'TERMINEE': Commande.objects.filter(etat=EtatCommande.TERMINEE).count(),
        'ANNULEE': Commande.objects.filter(etat=EtatCommande.ANNULEE).count(),
    }
    
    # Statistiques financières
    total_entrées = Paiement.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    total_sorties = Depense.objects.aggregate(total=models.Sum('montant'))['total'] or 0
    solde_net = total_entrées - total_sorties
    
    paiements_aujourdhui = Paiement.objects.filter(date_paiement__date=timezone.now().date())
    total_aujourdhui = paiements_aujourdhui.aggregate(total=models.Sum('montant'))['total'] or 0
    
    # Statistiques utilisateurs
    total_utilisateurs = User.objects.count()
    utilisateurs_par_role = {
        'Rtable': User.objects.filter(role='Rtable').count(),
        'Rserveur': User.objects.filter(role='Rserveur').count(),
        'Rcuisinier': User.objects.filter(role='Rcuisinier').count(),
        'Rcaissier': User.objects.filter(role='Rcaissier').count(),
        'Rcomptable': User.objects.filter(role='Rcomptable').count(),
        'Radmin': User.objects.filter(role='Radmin').count(),
    }
    
    # Activités récentes
    commandes_recentes = Commande.objects.order_by('-date_commande')[:5]
    paiements_recentes = Paiement.objects.order_by('-date_paiement')[:5]
    
    context = {
        'total_commandes': total_commandes,
        'commandes_aujourdhui': commandes_aujourdhui,
        'commandes_par_etat': commandes_par_etat,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
        'solde_net': solde_net,
        'total_aujourdhui': total_aujourdhui,
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_par_role': utilisateurs_par_role,
        'commandes_recentes': commandes_recentes,
        'paiements_recentes': paiements_recentes,
    }
    
    return render(request, 'restaurant/admin_dashboard.html', context)


# ==================== VUES QR CODE ====================

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def qr_code_list(request):
    """Liste des QR codes des tables"""
    qr_codes = QRCode.objects.select_related('table').all()
    
    context = {
        'qr_codes': qr_codes,
    }
    return render(request, 'restaurant/qr_code_list.html', context)

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def generer_qr_codes_toutes(request):
    """Générer des QR codes pour toutes les tables sans QR code"""
    tables_sans_qr = TableRestaurant.objects.filter(qr_code__isnull=True)
    tables_mises_a_jour = 0
    
    for table in tables_sans_qr:
        try:
            # Créer le QR code unique et permanent
            qr_code = QRCode.objects.create(
                table=table,
                code="TABLE_{}_{}".format(table.numero_table, table.id)  # Code unique permanent
            )
            qr_code.generer_qr_code()
            tables_mises_a_jour += 1
        except Exception as e:
            messages.error(request, "Erreur lors de la génération du QR code pour la table {}: {}".format(table.numero_table, str(e)))
    
    if tables_mises_a_jour > 0:
        messages.success(request, "{} QR codes générés avec succès !".format(tables_mises_a_jour))
    else:
        messages.info(request, "Toutes les tables ont déjà un QR code.")
    
    return redirect('restaurant:qr_code_list')

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def regenerer_qr_code(request, table_id):
    """Régénérer le QR code d'une table spécifique"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    try:
        # Récupérer ou créer le QR code
        qr_code, created = QRCode.objects.get_or_create(
            table=table,
            defaults={'code': "TABLE_{}_{}".format(table.numero_table, table.id)}
        )
        
        # Régénérer l'image du QR code
        qr_code.generer_qr_code()
        
        messages.success(request, "QR code de la table {} généré avec succès !".format(table.numero_table))
        
    except Exception as e:
        messages.error(request, "Erreur lors de la génération du QR code: {}".format(str(e)))
    
    return redirect('restaurant:qr_code_list')

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def desactiver_qr_code(request, table_id):
    """Désactiver un QR code"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    try:
        qr_code = QRCode.objects.get(table=table)
        qr_code.est_actif = False
        qr_code.save()
        messages.success(request, "QR code de la table {} désactivé.".format(table.numero_table))
        
    except QRCode.DoesNotExist:
        messages.error(request, "Aucun QR code trouvé pour la table {}.".format(table.numero_table))
    
    return redirect('restaurant:qr_code_list')

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def activer_qr_code(request, table_id):
    """Activer un QR code"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    try:
        qr_code = QRCode.objects.get(table=table)
        
        # Activer le QR code
        qr_code.est_actif = True
        qr_code.save()
        messages.success(request, "QR code de la table {} activé.".format(table.numero_table))
        
    except QRCode.DoesNotExist:
        messages.error(request, "Aucun QR code trouvé pour la table {}.".format(table.numero_table))
    
    return redirect('restaurant:qr_code_list')

def qr_menu_mobile(request, code):
    """Page du menu mobile accessible via QR code"""
    try:
        qr_code = QRCode.objects.get(code=code)
        
        # Vérifier si le QR code est actif
        if not qr_code.est_valide():
            return render(request, 'restaurant/qr_code_desactive.html', {
                'table': qr_code.table,
                'qr_code': qr_code
            })
        
        # Incrémenter le compteur d'utilisation
        qr_code.incrementer_utilisation()
        
        # Récupérer les plats actifs
        plats = Plat.objects.filter(disponible=True).order_by('categorie__nom', 'nom')
        categories = Categorie.objects.all()
        
        # Organiser les plats par catégorie
        plats_par_categorie = {}
        for plat in plats:
            categorie_nom = plat.categorie.nom
            if categorie_nom not in plats_par_categorie:
                plats_par_categorie[categorie_nom] = []
            plats_par_categorie[categorie_nom].append(plat)
        
        context = {
            'qr_code': qr_code,
            'table': qr_code.table,
            'plats_par_categorie': plats_par_categorie,
            'categories': categories,
            'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        }
        
        return render(request, 'restaurant/qr_menu_mobile.html', context)
        
    except QRCode.DoesNotExist:
        return render(request, 'restaurant/qr_code_non_trouve.html')
    except Exception as e:
        return render(request, 'restaurant/qr_code_erreur.html', {'erreur': str(e)})

@csrf_exempt
def api_generer_qr_code(request, table_id):
    """API pour générer un QR code pour une table spécifique"""
    try:
        # Vérifier si la table existe
        table = TableRestaurant.objects.filter(id=table_id).first()
        if not table:
            return JsonResponse({
                'success': False,
                'error': 'Table non trouvée'
            }, status=404)
        
        # Créer ou récupérer le QR code
        qr_code, created = QRCode.objects.get_or_create(
            table=table,
            defaults={'code': "TABLE_{}_{}".format(table.numero_table, table.id)}
        )
        
        # Générer l'image QR code
        qr_code.generer_qr_code()
        
        # Détection de l'environnement pour l'affichage
        from django.conf import settings
        
        production_url = getattr(settings, 'PRODUCTION_URL', None)
        
        if production_url and production_url != 'https://votre-app.onrender.com':
            # En production (Render) avec URL réelle
            base_url = production_url
            display_ip = production_url
        else:
            # En développement local ou fallback
            import socket
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip.startswith('127.'):
                    local_ip = "192.168.1.100"
            except:
                local_ip = "192.168.1.100"
            
            base_url = "http://{}:8000".format(local_ip)
            display_ip = local_ip
        
        return JsonResponse({
            'success': True,
            'qr_code_image': qr_code.qr_code_image,
            'table_number': table.numero_table,
            'table_id': table.id,
            'local_ip': display_ip,
            'url': "{}/restaurant/table/{}/".format(base_url, table.id),
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def menu_client_public(request, table_id):
    """Page publique du menu pour les clients qui scanment le QR Code"""
    try:
        table = get_object_or_404(TableRestaurant, id=table_id)
        
        # Récupérer tous les plats disponibles
        categories = Categorie.objects.filter(plat__isnull=False).distinct()
        menu_data = []
        
        for categorie in categories:
            plats = Plat.objects.filter(categorie=categorie, disponible=True)
            if plats.exists():
                menu_data.append({
                    'categorie': categorie,
                    'plats': plats
                })
        
        context = {
            'table': table,
            'menu_data': menu_data,
            'site_url': getattr(settings, 'PRODUCTION_URL', 'http://127.0.0.1:8000'),
        }
        
        return render(request, 'restaurant/menu_client_simple.html', context)
        
    except Exception as e:
        # Page d'erreur si la table n'existe pas
        return render(request, 'restaurant/qr_code_erreur.html', {'erreur': str(e)})

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def regenerer_tous_qr_codes_urls(request):
    """Régénérer tous les QR codes avec les nouvelles URLs vers les pages de tables"""
    try:
        qr_codes = QRCode.objects.all()
        count = 0
        
        for qr_code in qr_codes:
            try:
                qr_code.generer_qr_code()
                count += 1
            except Exception as e:
                messages.error(request, "Erreur pour la table {}: {}".format(qr_code.table.numero_table, str(e)))
        
        messages.success(request, "{} QR codes régénérés avec les nouvelles URLs vers les pages de tables".format(count))
        
    except Exception as e:
        messages.error(request, "Erreur lors de la régénération: {}".format(str(e)))
    
    return redirect('restaurant:qr_code_list')

@login_required
@admin_or_role_required('Radmin', 'Rserveur', 'Rcuisinier', 'Rcaissier', 'Rcomptable')
def imprimer_qr_code(request, table_id):
    """Page d'impression pour le QR code d'une table"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    try:
        qr_code = QRCode.objects.get(table=table)
        if not qr_code.qr_code_image:
            messages.error(request, "Aucun QR code généré pour cette table")
            return redirect('restaurant:table_detail', table_id=table_id)
        
        context = {
            'table_number': table.numero_table,
            'qr_code_image': qr_code.qr_code_image,
        }
        
        return render(request, 'restaurant/qr_print_template.html', context)
        
    except QRCode.DoesNotExist:
        messages.error(request, "Aucun QR code trouvé pour cette table")
        return redirect('restaurant:table_detail', table_id=table_id)
