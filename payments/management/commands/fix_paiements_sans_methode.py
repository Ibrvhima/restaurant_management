from django.core.management.base import BaseCommand
from django.db.models import Q
from payments.models import Paiement
from django.db import transaction

class Command(BaseCommand):
    help = 'Corrige les paiements sans méthode de paiement spécifiée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Montre les paiements à corriger sans les modifier',
        )
        parser.add_argument(
            '--methode-par-defaut',
            type=str,
            default='ESPECE',
            choices=['ESPECE', 'CARTE', 'MOBILE_MONEY', 'VIREMENT', 'CHEQUE'],
            help='Méthode de paiement à utiliser par défaut',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        methode_par_defaut = options['methode_par_defaut']
        
        # Trouver les paiements sans méthode
        paiements_sans_methode = Paiement.objects.filter(
            Q(methode__isnull=True) | Q(methode='')
        )
        
        count = paiements_sans_methode.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Tous les paiements ont déjà une méthode de paiement spécifiée!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  {count} paiement(s) trouvé(s) sans méthode de paiement:')
        )
        
        # Afficher les détails
        for paiement in paiements_sans_methode:
            self.stdout.write(
                f'  • Paiement #{paiement.id} - Commande #{paiement.commande.id} - '
                f'{paiement.montant} GNF - Date: {paiement.date_paiement.strftime("%d/%m/%Y %H:%M")}'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 Mode DRY RUN - Aucune modification effectuée')
            )
            self.stdout.write(
                f'Pour appliquer les corrections, exécutez: python manage.py fix_paiements_sans_methode --methode-par-defaut={methode_par_defaut}'
            )
        else:
            # Appliquer les corrections
            with transaction.atomic():
                updated = paiements_sans_methode.update(methode=methode_par_defaut)
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {updated} paiement(s) ont été mis à jour avec la méthode: {methode_par_defaut}')
            )
            
            self.stdout.write(
                self.style.SUCCESS('🎯 Tous les paiements ont maintenant une méthode de paiement spécifiée!')
            )
