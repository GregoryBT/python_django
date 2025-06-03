from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name=_("Nom"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    couleur = models.CharField(max_length=7, default='#007bff', help_text=_('Couleur en format hexadécimal (ex: #007bff)'), verbose_name=_("Couleur"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name=_("Nom"))
    slug = models.SlugField(max_length=50, unique=True, blank=True, verbose_name=_("Slug"))
    couleur = models.CharField(max_length=7, default='#6b7280', help_text=_('Couleur en format hexadécimal (ex: #6b7280)'), verbose_name=_("Couleur"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Profil(models.Model):
    """Modèle pour étendre les informations utilisateur avec des rôles"""
    ROLES = [
        ('lecteur', _('Lecteur')),
        ('auteur', _('Auteur')),
        ('moderateur', _('Modérateur')),
        ('admin', _('Administrateur')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', verbose_name=_("Utilisateur"))
    role = models.CharField(max_length=20, choices=ROLES, default='lecteur', verbose_name=_("Rôle"))
    bio = models.TextField(max_length=500, blank=True, help_text=_('Biographie de l\'utilisateur'), verbose_name=_("Biographie"))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text=_('Photo de profil'), verbose_name=_("Avatar"))
    site_web = models.URLField(blank=True, help_text=_('Site web personnel'), verbose_name=_("Site web"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name=_("Dernière connexion"))
    
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
        verbose_name = _("Profil")
        verbose_name_plural = _("Profils")


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
    titre = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, blank=True, verbose_name=_("Slug"))  # Temporairement non-unique
    contenu = models.TextField(verbose_name=_("Contenu"))
    auteur = models.CharField(max_length=100, verbose_name=_("Auteur"))  # Garder pour compatibilité
    user_auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='articles', verbose_name=_("Utilisateur auteur"))  # Nouveau champ
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name=_("Catégorie"))
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name=_("Tags"))
    image = models.ImageField(upload_to='articles/', null=True, blank=True, help_text=_('Image d\'illustration pour l\'article'), verbose_name=_("Image"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    nombre_vues = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de vues"))  # Compteur simple de vues
    est_publie = models.BooleanField(default=True, help_text=_('Article visible publiquement'), verbose_name=_("Est publié"))
    
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

    def get_auteur_display(self):
        """Retourne le nom de l'auteur à afficher"""
        if self.user_auteur:
            # Si l'article a un utilisateur assigné, utiliser son nom complet ou username
            if self.user_auteur.first_name and self.user_auteur.last_name:
                return f"{self.user_auteur.first_name} {self.user_auteur.last_name}"
            else:
                return self.user_auteur.username
        else:
            # Sinon, utiliser le champ auteur classique
            return self.auteur or "Auteur inconnu"
    
    def get_nom_auteur(self):
        """Alias pour get_auteur_display pour compatibilité"""
        return self.get_auteur_display()

    class Meta:
        ordering = ['-date_creation']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class VueArticle(models.Model):
    """Modèle pour tracker les vues individuelles des articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='vues', verbose_name=_("Article"))
    adresse_ip = models.GenericIPAddressField(verbose_name=_("Adresse IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))  # Navigateur/appareil utilisé
    date_vue = models.DateTimeField(default=timezone.now, verbose_name=_("Date de vue"))

    def __str__(self):
        return f'Vue de {self.article.titre} le {self.date_vue.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['-date_vue']
        # Éviter les doublons pour la même IP dans un court laps de temps
        unique_together = ['article', 'adresse_ip', 'date_vue']
        verbose_name = _("Vue d'article")
        verbose_name_plural = _("Vues d'articles")


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires', verbose_name=_("Article"))
    nom_auteur = models.CharField(max_length=100, verbose_name=_("Nom de l'auteur"))  # Garder pour compatibilité
    user_auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='commentaires', verbose_name=_("Utilisateur auteur"))  # Nouveau champ
    contenu = models.TextField(verbose_name=_("Contenu"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    est_approuve = models.BooleanField(default=True, help_text=_('Commentaire approuvé par la modération'), verbose_name=_("Est approuvé"))
    
    def save(self, *args, **kwargs):
        # Si on a un user_auteur, utiliser son nom comme nom_auteur
        if self.user_auteur and not self.nom_auteur:
            self.nom_auteur = f"{self.user_auteur.first_name} {self.user_auteur.last_name}".strip() or self.user_auteur.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Commentaire de {self.nom_auteur} sur {self.article.titre}'

    def get_nom_auteur(self):
        """Retourne le nom de l'auteur du commentaire à afficher"""
        if self.user_auteur:
            # Si le commentaire a un utilisateur assigné, utiliser son nom complet ou username
            if self.user_auteur.first_name and self.user_auteur.last_name:
                return f"{self.user_auteur.first_name} {self.user_auteur.last_name}"
            else:
                return self.user_auteur.username
        else:
            # Sinon, utiliser le champ nom_auteur classique
            return self.nom_auteur or "Auteur inconnu"

    class Meta:
        ordering = ['-date_creation']
        verbose_name = _("Commentaire")
        verbose_name_plural = _("Commentaires")