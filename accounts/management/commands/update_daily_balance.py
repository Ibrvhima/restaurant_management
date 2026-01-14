from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.email_utils import update_daily_balance

class Command(BaseCommand):
    help = 'Mettre à jour le solde de caisse quotidien et envoyer les rapports par email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date pour laquelle mettre à jour le solde (format: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Exécuter en mode test (envoyer seulement au premier admin)',
        )

    def handle(self, *args, **options):
        # Récupérer la date
        if options['date']:
            try:
                from datetime import datetime
                date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Format de date invalide. Utilisez YYYY-MM-DD')
                )
                return
        else:
            date = timezone.now().date()
        
        self.stdout.write(f'Mise à jour du solde pour la date: {date}')
        
        # Exécuter la mise à jour
        result = update_daily_balance(date)
        
        # Afficher les résultats
        self.stdout.write(self.style.SUCCESS('=== RAPPORT DE MISE À JOUR ==='))
        self.stdout.write(f'Date: {result["date"]}')
        self.stdout.write(f'Solde du jour: {result["solde_jour"]:,.0f} GNF')
        self.stdout.write(f'Solde cumulé: {result["solde_cumul"]:,.0f} GNF')
        self.stdout.write(f'Total entrées: {result["total_entrées"]:,.0f} GNF')
        self.stdout.write(f'Total sorties: {result["total_sorties"]:,.0f} GNF')
        
        if result['rapport_envoye']:
            self.stdout.write(self.style.SUCCESS('✅ Rapport quotidien envoyé par email'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Échec de l\'envoi du rapport'))
        
        if result['alerte_envoyee']:
            self.stdout.write(self.style.WARNING('⚠️ Alerte de solde critique envoyée'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Aucune alerte nécessaire'))
        
        self.stdout.write(self.style.SUCCESS('=== FIN DU RAPPORT ==='))
