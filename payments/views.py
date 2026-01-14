from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, date
from .models import Paiement, MethodePaiement, Caisse

from django.core.paginator import Paginator
from datetime import datetime

@login_required
def paiement_list(request):
    """Liste des paiements"""
    paiements = Paiement.objects.all()
    
    # Gérer le tri
    sort_field = request.GET.get('sort')
    if sort_field:
        if sort_field == 'id':
            paiements = paiements.order_by('id')
        elif sort_field == 'commande':
            paiements = paiements.order_by('commande__id')
        elif sort_field == 'caissier':
            paiements = paiements.order_by('caissier__login')
        elif sort_field == 'montant':
            paiements = paiements.order_by('montant')
        elif sort_field == 'date':
            paiements = paiements.order_by('date_paiement')
        else:
            paiements = paiements.order_by('-date_paiement')
    else:
        paiements = paiements.order_by('-date_paiement')
    
    # Filtrer par méthode si spécifié
    methode = request.GET.get('methode')
    if methode:
        paiements = paiements.filter(methode=methode)
    
    # Filtrer par date si spécifié
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            paiements = paiements.filter(date_paiement__date=filter_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(paiements, 20)  # 20 paiements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    methodes = MethodePaiement.choices
    context = {
        'paiements': page_obj,
        'methodes': methodes,
        'methode_filter': methode,
        'date_filter': date_filter,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'payments/paiement_list.html', context)

@login_required
def paiement_detail(request, paiement_id):
    """Détail d'un paiement"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    return render(request, 'payments/paiement_detail.html', {'paiement': paiement})

@login_required
def nouveau_paiement(request):
    """Créer un nouveau paiement"""
    # Seul le serveur peut valider un paiement
    if request.user.role != 'Rserveur':
        messages.error(request, "Seul le serveur peut valider un paiement.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        commande_id = request.POST.get('commande')
        methode = request.POST.get('methode')
        montant = request.POST.get('montant')
        
        if not commande_id or not methode or not montant:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return redirect('payments:nouveau_paiement')
        
        try:
            montant = float(montant)
            if montant <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Montant invalide.')
            return redirect('payments:nouveau_paiement')
        
        # Créer le paiement
        paiement = Paiement.objects.create(
            commande_id=commande_id,
            methode=methode,
            montant=montant,
            caissier=request.user
        )
        
        messages.success(request, f'Paiement #{paiement.id} enregistré avec succès!')
        return redirect('payments:paiement_detail', paiement_id=paiement.id)
    
    # Récupérer les commandes non payées
    from orders.models import Commande, EtatCommande
    commandes = Commande.objects.exclude(
        id__in=Paiement.objects.values_list('commande_id', flat=True)
    ).filter(
        etat__in=[EtatCommande.TERMINEE, EtatCommande.EN_COURS, EtatCommande.EN_PREPARATION]
    ).order_by('-date_commande')
    
    methodes = MethodePaiement.choices
    context = {
        'commandes': commandes,
        'methodes': methodes
    }
    return render(request, 'payments/nouveau_paiement.html', context)

@login_required
def caisse_dashboard(request):
    """Tableau de bord de la caisse"""
    caisse = Caisse.get_instance()
    
    # Statistiques du jour
    today = timezone.now().date()
    paiements_aujourdhui = Paiement.objects.filter(date_paiement__date=today)
    total_aujourdhui = paiements_aujourdhui.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_paiements_aujourdhui = paiements_aujourdhui.count()
    
    # Importer les dépenses pour calculer les sorties
    from expenses.models import Depense
    depenses_aujourdhui = Depense.objects.filter(date_depense=today)
    total_sorties_aujourdhui = depenses_aujourdhui.aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Calculer le solde actuel (entrées - sorties)
    solde_calculé = total_aujourdhui - total_sorties_aujourdhui
    
    # Statistiques par méthode (simplifié)
    stats_par_methode = []
    for methode_choice, methode_label in MethodePaiement.choices:
        paiements_methode = paiements_aujourdhui.filter(methode=methode_choice)
        total_methode = paiements_methode.aggregate(Sum('montant'))['montant__sum'] or 0
        count_methode = paiements_methode.count()
        stats_par_methode.append({
            'methode': methode_choice,
            'methode_label': methode_label,
            'total': total_methode,
            'count': count_methode
        })
    
    # Trier par total décroissant
    stats_par_methode.sort(key=lambda x: x['total'], reverse=True)
    
    context = {
        'caisse': caisse,
        'total_aujourdhui': total_aujourdhui,
        'total_sorties_aujourdhui': total_sorties_aujourdhui,
        'solde_calculé': solde_calculé,
        'nb_paiements_aujourdhui': nb_paiements_aujourdhui,
        'stats_par_methode': stats_par_methode
    }
    
    return render(request, 'payments/caisse_dashboard.html', context)

@require_POST
@login_required
def ajouter_montant_caisse(request):
    """Ajouter un montant à la caisse"""
    montant = request.POST.get('montant')
    
    if not montant:
        messages.error(request, 'Veuillez spécifier un montant.')
        return redirect('payments:caisse_dashboard')
    
    try:
        from decimal import Decimal
        montant = Decimal(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        messages.error(request, 'Montant invalide.')
        return redirect('payments:caisse_dashboard')
    
    caisse = Caisse.get_instance()
    caisse.ajouter_montant(montant)
    
    messages.success(request, f'{montant} FCFA ajoutés à la caisse.')
    return redirect('payments:caisse_dashboard')

@require_POST
@login_required
def retirer_montant_caisse(request):
    """Retirer un montant de la caisse"""
    montant = request.POST.get('montant')
    
    if not montant:
        messages.error(request, 'Veuillez spécifier un montant.')
        return redirect('payments:caisse_dashboard')
    
    try:
        montant = float(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        messages.error(request, 'Montant invalide.')
        return redirect('payments:caisse_dashboard')
    
    caisse = Caisse.get_instance()
    if caisse.solde_actuel >= montant:
        caisse.retirer_montant(montant)
        messages.success(request, f'{montant} FCFA retirés de la caisse.')
    else:
        messages.error(request, 'Solde insuffisant dans la caisse.')
    
    return redirect('payments:caisse_dashboard')

@login_required
def rapport_paiements(request):
    """Rapport des paiements"""
    # Période par défaut : ce mois
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    date_debut = request.GET.get('date_debut', month_start)
    date_fin = request.GET.get('date_fin', today)
    
    try:
        if isinstance(date_debut, str):
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if isinstance(date_fin, str):
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    except ValueError:
        date_debut = month_start
        date_fin = today
    
    paiements = Paiement.objects.filter(
        date_paiement__date__gte=date_debut,
        date_paiement__date__lte=date_fin
    )
    
    # Statistiques
    total = paiements.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_paiements = paiements.count()
    
    # Par méthode
    stats_par_methode = []
    methode_stats = paiements.values('methode').annotate(
        total=Sum('montant'),
        count=Count('id')
    ).order_by('-total')
    
    # Convertir les dictionnaires en objets simples et normaliser les méthodes
    for stat in methode_stats:
        methode = stat['methode']
        if methode == 'ESPECE':
            methode_affichage = 'Espèce'
        elif methode == 'CARTE':
            methode_affichage = 'Carte bancaire'
        elif methode == 'MOBILE_MONEY':
            methode_affichage = 'Mobile money'
        elif methode == 'VIREMENT':
            methode_affichage = 'Virement bancaire'
        elif methode == 'CHEQUE':
            methode_affichage = 'Chèque'
        else:
            methode_affichage = methode
        
        stats_par_methode.append({
            'methode': methode,
            'methode_affichage': methode_affichage,
            'total': stat['total'],
            'count': stat['count']
        })
    
    context = {
        'paiements': paiements,
        'total': total,
        'nb_paiements': nb_paiements,
        'stats_par_methode': stats_par_methode,
        'date_debut': date_debut,
        'date_fin': date_fin
    }
    
    return render(request, 'payments/rapport_paiements.html', context)
