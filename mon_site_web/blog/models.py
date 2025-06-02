from django.db import models
from django.utils import timezone

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


class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    auteur = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-date_creation']


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    nom_auteur = models.CharField(max_length=100)
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Commentaire de {self.nom_auteur} sur {self.article.titre}'

    class Meta:
        ordering = ['date_creation']