from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#007bff', help_text='Couleur en format hexadécimal (ex: #007bff)')
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    couleur = models.CharField(max_length=7, default='#6b7280', help_text='Couleur en format hexadécimal (ex: #6b7280)')
    date_creation = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)  # Temporairement non-unique
    contenu = models.TextField()
    auteur = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    image = models.ImageField(upload_to='articles/', null=True, blank=True, help_text='Image d\'illustration pour l\'article')
    date_creation = models.DateTimeField(default=timezone.now)
    nombre_vues = models.PositiveIntegerField(default=0)  # Compteur simple de vues

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def incrementer_vues(self):
        """Incrémente le compteur de vues"""
        self.nombre_vues += 1
        self.save(update_fields=['nombre_vues'])

    class Meta:
        ordering = ['-date_creation']


class VueArticle(models.Model):
    """Modèle pour tracker les vues individuelles des articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='vues')
    adresse_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)  # Navigateur/appareil utilisé
    date_vue = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Vue de {self.article.titre} le {self.date_vue.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['-date_vue']
        # Éviter les doublons pour la même IP dans un court laps de temps
        unique_together = ['article', 'adresse_ip', 'date_vue']


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    nom_auteur = models.CharField(max_length=100)
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Commentaire de {self.nom_auteur} sur {self.article.titre}'

    class Meta:
        ordering = ['date_creation']