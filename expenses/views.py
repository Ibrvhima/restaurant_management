from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, date
from .models import Depense, CategorieDepense

@login_required
def depense_list(request):
    """Liste des dépenses"""
    depenses = Depense.objects.all().order_by('-date_depense')
    
    # Filtrer par catégorie si spécifié
    categorie = request.GET.get('categorie')
    if categorie:
        depenses = depenses.filter(categorie_id=categorie)
    
    # Filtrer par date si spécifié
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            depenses = depenses.filter(date_depense__date=filter_date)
        except ValueError:
            pass
    
    # Calculer les statistiques
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Importer les paiements pour calculer les entrées
    from payments.models import Paiement
    paiements = Paiement.objects.all()
    
    # Filtrer les paiements par date si nécessaire
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            paiements = paiements.filter(date_paiement__date=filter_date)
        except ValueError:
            pass
    
    total_entrees = paiements.aggregate(Sum('montant'))['montant__sum'] or 0
    solde_actuel = total_entrees - total_depenses
    
    categories = CategorieDepense.objects.all()
    context = {
        'depenses': depenses,
        'categories': categories,
        'categorie_filter': categorie,
        'date_filter': date_filter,
        'total_depenses': total_depenses,
        'total_entrees': total_entrees,
        'solde_actuel': solde_actuel
    }
    return render(request, 'expenses/depense_list.html', context)

@login_required
def depense_detail(request, depense_id):
    """Détail d'une dépense"""
    depense = get_object_or_404(Depense, id=depense_id)
    return render(request, 'expenses/depense_detail.html', {'depense': depense})

@login_required
def nouvelle_depense(request):
    """Créer une nouvelle dépense"""
    if request.method == 'POST':
        description = request.POST.get('description')
        montant = request.POST.get('montant')
        categorie_id = request.POST.get('categorie')
        date_depense = request.POST.get('date_depense')
        
        if not description or not montant or not categorie_id:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('expenses:nouvelle_depense')
        
        try:
            montant = float(montant)
            if montant <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Montant invalide.')
            return redirect('expenses:nouvelle_depense')
        
        # Gérer la date
        if date_depense:
            try:
                date_depense = datetime.strptime(date_depense, '%Y-%m-%d').date()
            except ValueError:
                date_depense = timezone.now().date()
        else:
            date_depense = timezone.now().date()
        
        # Créer la dépense
        depense = Depense.objects.create(
            description=description,
            montant=montant,
            categorie_id=categorie_id,
            date_depense=date_depense,
            utilisateur=request.user
        )
        
        messages.success(request, f'Dépense #{depense.id} enregistrée avec succès!')
        return redirect('depense_detail', depense_id=depense.id)
    
    categories = CategorieDepense.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'expenses/nouvelle_depense.html', context)

@login_required
def modifier_depense(request, depense_id):
    """Modifier une dépense"""
    depense = get_object_or_404(Depense, id=depense_id)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        montant = request.POST.get('montant')
        categorie_id = request.POST.get('categorie')
        date_depense = request.POST.get('date_depense')
        
        if not description or not montant or not categorie_id:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('modifier_depense', depense_id=depense.id)
        
        try:
            montant = float(montant)
            if montant <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Montant invalide.')
            return redirect('modifier_depense', depense_id=depense.id)
        
        # Gérer la date
        if date_depense:
            try:
                date_depense = datetime.strptime(date_depense, '%Y-%m-%d').date()
            except ValueError:
                date_depense = depense.date_depense
        
        # Mettre à jour la dépense
        depense.description = description
        depense.montant = montant
        depense.categorie_id = categorie_id
        depense.date_depense = date_depense
        depense.save()
        
        messages.success(request, f'Dépense #{depense.id} mise à jour avec succès!')
        return redirect('depense_detail', depense_id=depense.id)
    
    categories = CategorieDepense.objects.all()
    context = {
        'depense': depense,
        'categories': categories
    }
    return render(request, 'expenses/modifier_depense.html', context)

@require_POST
@login_required
def supprimer_depense(request, depense_id):
    """Supprimer une dépense"""
    depense = get_object_or_404(Depense, id=depense_id)
    depense.delete()
    messages.success(request, f'Dépense #{depense_id} supprimée avec succès!')
    return redirect('expenses:depense_list')

@login_required
def statistiques_depenses(request):
    """Statistiques des dépenses"""
    today = timezone.now().date()
    
    # Statistiques du jour
    depenses_aujourdhui = Depense.objects.filter(date_depense=today)
    total_aujourdhui = depenses_aujourdhui.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_depenses_aujourdhui = depenses_aujourdhui.count()
    
    # Statistiques du mois
    month_start = today.replace(day=1)
    depenses_mois = Depense.objects.filter(date_depense__gte=month_start)
    total_mois = depenses_mois.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_depenses_mois = depenses_mois.count()
    
    # Par catégorie
    stats_par_categorie = []
    categorie_stats = depenses_mois.values('categorie__nom').annotate(
        total=Sum('montant'),
        count=Count('id')
    ).order_by('-total')
    
    # Convertir les dictionnaires en objets simples
    for stat in categorie_stats:
        stats_par_categorie.append({
            'categorie_nom': stat['categorie__nom'] or 'Non catégorisé',
            'total': stat['total'],
            'count': stat['count']
        })
    
    context = {
        'total_aujourdhui': total_aujourdhui,
        'nb_depenses_aujourdhui': nb_depenses_aujourdhui,
        'total_mois': total_mois,
        'nb_depenses_mois': nb_depenses_mois,
        'stats_par_categorie': stats_par_categorie
    }
    
    return render(request, 'expenses/statistiques.html', context)

@login_required
def rapport_depenses(request):
    """Rapport des dépenses"""
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
    
    depenses = Depense.objects.filter(
        date_depense__gte=date_debut,
        date_depense__lte=date_fin
    )
    
    # Statistiques
    total = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    nb_depenses = depenses.count()
    
    # Par catégorie
    stats_par_categorie = []
    categorie_stats = depenses.values('categorie__nom').annotate(
        total=Sum('montant'),
        count=Count('id')
    ).order_by('-total')
    
    # Convertir les dictionnaires en objets simples
    for stat in categorie_stats:
        stats_par_categorie.append({
            'categorie_nom': stat['categorie__nom'] or 'Non catégorisé',
            'total': stat['total'],
            'count': stat['count']
        })
    
    context = {
        'depenses': depenses,
        'total': total,
        'nb_depenses': nb_depenses,
        'stats_par_categorie': stats_par_categorie,
        'date_debut': date_debut,
        'date_fin': date_fin
    }
    
    return render(request, 'expenses/rapport_depenses.html', context)
