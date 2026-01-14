from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from .models import Plat, TableRestaurant, Categorie
from .forms import PlatForm, CategorieForm
from orders.models import Commande, EtatCommande
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json

def menu_list(request):
    """Liste des plats du menu avec filtres"""
    # Récupérer les paramètres de filtre
    search_query = request.GET.get('search', '')
    type_plat_filter = request.GET.get('type_plat', '')
    categorie_filter = request.GET.get('categorie', '')
    
    # Filtrer les plats de base
    plats = Plat.objects.filter(disponible=True)
    
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
def liste_categories(request):
    """Liste des catégories (réservé au cuisinier et admin)"""
    if not (request.user.is_cuisinier() or request.user.is_admin()):
        messages.error(request, "Vous n'avez pas les permissions pour gérer les catégories.")
        return redirect('restaurant:menu_list')
    
    categories = Categorie.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'restaurant/liste_categories.html', context)


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
@login_required
def table_home(request):
    """Page d'accueil pour les tables"""
    if request.user.role != 'Rtable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    # Récupérer la table associée à l'utilisateur
    try:
        table = request.user.table
    except TableRestaurant.DoesNotExist:
        messages.error(request, "Aucune table associée à votre compte.")
        return redirect('accounts:login')
    
    # Récupérer les plats disponibles
    plats = Plat.objects.filter(disponible=True).order_by('nom')
    categories = Categorie.objects.all()
    
    context = {
        'table': table,
        'plats': plats,
        'categories': categories
    }
    return render(request, 'restaurant/table_home.html', context)


@login_required
def table_panier(request):
    """Gestion du panier pour les tables"""
    if request.user.role != 'Rtable':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
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


@login_required
def table_valider_commande(request):
    """Validation du panier et création de commande"""
    if request.user.role != 'Rtable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    panier = request.session.get('panier', {})
    
    if not panier:
        messages.error(request, "Votre panier est vide.")
        return redirect('restaurant:table_home')
    
    try:
        table = request.user.table
    except TableRestaurant.DoesNotExist:
        messages.error(request, "Aucune table associée à votre compte.")
        return redirect('accounts:login')
    
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


@login_required
def serveur_home(request):
    """Page d'accueil pour les serveurs"""
    if request.user.role != 'Rserveur':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def serveur_table_commandes(request, table_id):
    """Consultation des commandes d'une table spécifique"""
    if request.user.role != 'Rserveur':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    commandes = Commande.objects.filter(table=table).select_related('paiement').order_by('-date_commande')
    
    context = {
        'table': table,
        'commandes': commandes
    }
    return render(request, 'restaurant/serveur_table_commandes.html', context)


@login_required
def serveur_valider_service(request, commande_id):
    """Validation du service (plats servis)"""
    if request.user.role != 'Rserveur':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def cuisinier_home(request):
    """Page d'accueil pour les cuisiniers"""
    if request.user.role != 'Rcuisinier':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def cuisinier_prendre_commande(request, commande_id):
    """Prendre une commande en charge (EN_ATTENTE → EN_PREPARATION)"""
    if request.user.role != 'Rcuisinier':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def cuisinier_changer_etat(request, commande_id):
    """Changer l'état d'une commande (EN_PREPARATION ↔ EN_COURS)"""
    if request.user.role != 'Rcuisinier':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def cuisinier_marquer_prete(request, commande_id):
    """Marquer une commande comme prête pour livraison (EN_COURS → TERMINEE)"""
    if request.user.role != 'Rcuisinier':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def comptable_home(request):
    """Page d'accueil pour les comptables"""
    if request.user.role != 'Rcomptable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def comptable_commandes(request):
    """Consultation de la liste des commandes"""
    if request.user.role not in ['Rcomptable', 'Rserveur']:
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    commandes = Commande.objects.all().order_by('-date_commande')
    
    context = {
        'commandes': commandes
    }
    return render(request, 'restaurant/comptable_commandes.html', context)


@login_required
def comptable_paiements(request):
    """Consultation des paiements"""
    if request.user.role != 'Rcomptable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    from payments.models import Paiement
    paiements = Paiement.objects.all().order_by('-date_paiement')
    
    context = {
        'paiements': paiements
    }
    return render(request, 'restaurant/comptable_paiements.html', context)


@login_required
def comptable_nouvelle_depense(request):
    """Enregistrement d'une nouvelle dépense"""
    if request.user.role != 'Rcomptable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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


@login_required
def serveur_valider_paiement(request, commande_id):
    """Validation du paiement"""
    if request.user.role != 'Rserveur':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        from payments.models import Paiement
        paiement, created = Paiement.objects.get_or_create(
            commande=commande,
            defaults={
                'montant': commande.total,
                'methode': request.POST.get('methode', 'Espece'),
                'date_paiement': timezone.now()
            }
        )
        
        if created:
            messages.success(request, f"Paiement de la commande #{commande.id} enregistré.")
        else:
            messages.info(request, f"Paiement de la commande #{commande.id} déjà existant.")
        
        # Rediriger vers la page des commandes de la table pour voir l'état mis à jour
        return redirect('restaurant:serveur_table_commandes', table_id=commande.table.id)
    
    context = {
        'commande': commande
    }
    return render(request, 'restaurant/serveur_valider_paiement.html', context)


@login_required
def table_commandes(request):
    """Liste des commandes de la table"""
    if request.user.role != 'Rtable':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:login')
    
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
                    'sous_total': str(cp.sous_total())
                })
            
            commandes_data.append({
                'id': commande.id,
                'table_numero': commande.table.numero_table,
                'etat': commande.etat,
                'etat_display': commande.get_etat_display(),
                'heure': commande.date_commande.strftime('%H:%M'),
                'total': str(commande.total),
                'plats': plats_data,
                'temps_estime': temps_estime
            })
        
        return JsonResponse({
            'success': True,
            'commandes': commandes_data,
            'total': len(commandes_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la récupération des commandes: {str(e)}'
        }, status=500)
