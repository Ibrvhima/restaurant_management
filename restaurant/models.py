from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Categorie(models.Model):
    """
    Modèle pour les catégories de plats
    """
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class TableRestaurant(models.Model):
    """
    Modèle pour les tables du restaurant
    """
    numero_table = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Numéro de table'
    )
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Nombre de places',
        default=4
    )
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='table',
        limit_choices_to={'role': 'Rtable'},
        verbose_name='Utilisateur associé',
        null=True,
        blank=True
    )
    est_occupee = models.BooleanField(
        default=False,
        verbose_name='Table occupée'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tables_restaurant'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['numero_table']
    
    def __str__(self):
        return f"Table {self.numero_table} ({self.nombre_places} places)"


class Plat(models.Model):
    """
    Modèle pour les plats du restaurant
    """
    TYPE_PLAT_CHOICES = [
        ('entree', 'Entrée'),
        ('principal', 'Plat principal'),
        ('special', 'Plat spécial'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
        ('accompagnement', 'Accompagnement'),
    ]
    
    nom = models.CharField(
        max_length=200,
        verbose_name='Nom du plat'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Prix unitaire'
    )
    type_plat = models.CharField(
        max_length=20,
        choices=TYPE_PLAT_CHOICES,
        default='principal',
        verbose_name='Type de plat'
    )
    image = models.ImageField(
        upload_to='plats/',
        blank=True,
        null=True,
        verbose_name='Image du plat'
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name='Disponible'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Catégorie'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plats'
        verbose_name = 'Plat'
        verbose_name_plural = 'Plats'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} - {self.prix_unitaire} FCFA"

class Panier(models.Model):
    """
    Modèle pour les paniers (temporaire, lié à une table)
    """
    table = models.OneToOneField(
        TableRestaurant,
        on_delete=models.CASCADE,
        related_name='panier',
        verbose_name='Table'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paniers'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Panier Table {self.table.numero_table}"

class PanierItem(models.Model):
    """
    Modèle pour les items dans un panier
    """
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Panier'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE,
        verbose_name='Plat'
    )
    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantité'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'panier_items'
        verbose_name = 'Item du panier'
        verbose_name_plural = 'Items du panier'
        unique_together = ['panier', 'plat']
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.plat.nom} x{self.quantite}"
    
    def sous_total(self):
        """Calcule le sous-total de l'item"""
        return self.prix_unitaire * self.quantite
