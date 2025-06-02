from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class Profil(models.Model):
    """Modèle pour étendre les informations utilisateur avec des rôles"""
    ROLES = [
        ('lecteur', 'Lecteur'),
        ('auteur', 'Auteur'),
        ('moderateur', 'Modérateur'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLES, default='lecteur')
    bio = models.TextField(max_length=500, blank=True, help_text='Biographie de l\'utilisateur')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text='Photo de profil')
    site_web = models.URLField(blank=True, help_text='Site web personnel')
    date_creation = models.DateTimeField(default=timezone.now)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
    
    def peut_creer_article(self):
        """Vérifie si l'utilisateur peut créer des articles"""
        return self.role in ['auteur', 'moderateur', 'admin']
    
    def peut_moderer(self):
        """Vérifie si l'utilisateur peut modérer (supprimer commentaires, etc.)"""
        return self.role in ['moderateur', 'admin']
    
    def est_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin'
    
    class Meta:
        ordering = ['-date_creation']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil quand un utilisateur est créé"""
    if created:
        Profil.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil quand l'utilisateur est sauvegardé"""
    if hasattr(instance, 'profil'):
        instance.profil.save()


class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)  # Temporairement non-unique
    contenu = models.TextField()
    auteur = models.CharField(max_length=100)  # Garder pour compatibilité
    user_auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='articles')  # Nouveau champ
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    image = models.ImageField(upload_to='articles/', null=True, blank=True, help_text='Image d\'illustration pour l\'article')
    date_creation = models.DateTimeField(default=timezone.now)
    nombre_vues = models.PositiveIntegerField(default=0)  # Compteur simple de vues
    est_publie = models.BooleanField(default=True, help_text='Article visible publiquement')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        # Si on a un user_auteur, utiliser son nom comme auteur
        if self.user_auteur and not self.auteur:
            self.auteur = f"{self.user_auteur.first_name} {self.user_auteur.last_name}".strip() or self.user_auteur.username
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
    nom_auteur = models.CharField(max_length=100)  # Garder pour compatibilité
    user_auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='commentaires')  # Nouveau champ
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    est_approuve = models.BooleanField(default=True, help_text='Commentaire approuvé par la modération')
    
    def save(self, *args, **kwargs):
        # Si on a un user_auteur, utiliser son nom comme nom_auteur
        if self.user_auteur and not self.nom_auteur:
            self.nom_auteur = f"{self.user_auteur.first_name} {self.user_auteur.last_name}".strip() or self.user_auteur.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Commentaire de {self.nom_auteur} sur {self.article.titre}'

    class Meta:
        ordering = ['date_creation']