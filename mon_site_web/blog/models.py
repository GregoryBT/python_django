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
        ('utilisateur', _('Utilisateur')),
        ('administrateur', _('Administrateur')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', verbose_name=_("Utilisateur"))
    role = models.CharField(max_length=20, choices=ROLES, default='utilisateur', verbose_name=_("Rôle"))
    bio = models.TextField(max_length=500, blank=True, help_text=_('Biographie de l\'utilisateur'), verbose_name=_("Biographie"))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text=_('Photo de profil'), verbose_name=_("Avatar"))
    site_web = models.URLField(blank=True, help_text=_('Site web personnel'), verbose_name=_("Site web"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name=_("Dernière connexion"))
    
    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
    
    def peut_creer_article(self):
        """Vérifie si l'utilisateur peut créer des articles"""
        # Tous les utilisateurs connectés peuvent créer des articles
        return True
    
    def peut_modifier_article(self, article):
        """Vérifie si l'utilisateur peut modifier un article spécifique"""
        # Administrateur peut tout modifier, utilisateur peut modifier ses propres articles
        if self.role == 'administrateur':
            return True
        return article.user_auteur == self.user
    
    def peut_supprimer_article(self, article):
        """Vérifie si l'utilisateur peut supprimer un article spécifique"""
        # Administrateur peut tout supprimer, utilisateur peut supprimer ses propres articles
        if self.role == 'administrateur':
            return True
        return article.user_auteur == self.user
    
    def peut_moderer(self):
        """Vérifie si l'utilisateur peut modérer (supprimer commentaires, etc.)"""
        # Seuls les administrateurs peuvent modérer
        return self.role == 'administrateur'
    
    def est_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'administrateur'
    
    def peut_voir_article(self, article):
        """Vérifie si l'utilisateur peut voir un article spécifique"""
        # Article publié : tout le monde peut voir
        if article.est_publie:
            return True
        # Article non publié : administrateur ou auteur de l'article
        if self.role == 'administrateur':
            return True
        return article.user_auteur == self.user
    
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

    def get_auteur_username(self):
        """Retourne le nom d'utilisateur de l'auteur pour les liens de profil"""
        if self.user_auteur:
            return self.user_auteur.username
        else:
            # Si pas d'utilisateur lié, on ne peut pas faire de lien
            return None

    def calculer_temps_lecture(self):
        """Calcule le temps de lecture estimé en minutes (100 mots = 1 minute)"""
        import re
        from django.utils.html import strip_tags
        
        # Nettoyer le contenu HTML et compter les mots
        contenu_propre = strip_tags(self.contenu)
        # Remplacer les caractères de ponctuation et espaces multiples
        contenu_propre = re.sub(r'[^\w\s]', ' ', contenu_propre)
        contenu_propre = re.sub(r'\s+', ' ', contenu_propre).strip()
        
        # Compter les mots (diviser par les espaces)
        if not contenu_propre:
            return 1  # Minimum 1 minute
        
        mots = len(contenu_propre.split())
        
        # Calculer le temps en minutes (100 mots = 1 minute)
        temps_minutes = max(1, round(mots / 100))
        
        return temps_minutes

    def get_temps_lecture_display(self):
        """Retourne le temps de lecture formaté pour l'affichage"""
        temps = self.calculer_temps_lecture()
        if temps == 1:
            return "1 min"
        else:
            return f"{temps} min"

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

    def get_auteur_username(self):
        """Retourne le username de l'auteur du commentaire s'il s'agit d'un utilisateur"""
        if self.user_auteur:
            return self.user_auteur.username
        return None

    def nombre_likes(self):
        """Retourne le nombre de likes pour ce commentaire"""
        return self.likes_commentaire.count()

    def est_like_par_user(self, user):
        """Vérifie si un utilisateur a liké ce commentaire"""
        if not user.is_authenticated:
            return False
        return self.likes_commentaire.filter(user=user).exists()

    class Meta:
        ordering = ['-date_creation']
        verbose_name = _("Commentaire")
        verbose_name_plural = _("Commentaires")


class Like(models.Model):
    """Modèle pour gérer les likes des articles par les utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name=_("Utilisateur"))
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes', verbose_name=_("Article"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    
    def __str__(self):
        return f'{self.user.username} aime {self.article.titre}'
    
    class Meta:
        unique_together = ('user', 'article')  # Un utilisateur ne peut liker qu'une fois le même article
        ordering = ['-date_creation']
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")


class Bookmark(models.Model):
    """Modèle pour gérer les favoris/bookmarks des articles par les utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_("Utilisateur"))
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_("Article"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    note_personnelle = models.TextField(blank=True, max_length=500, help_text=_('Note personnelle sur cet article'), verbose_name=_("Note personnelle"))
    
    def __str__(self):
        return f'{self.user.username} a mis en favoris {self.article.titre}'
    
    class Meta:
        unique_together = ('user', 'article')  # Un utilisateur ne peut bookmarker qu'une fois le même article
        ordering = ['-date_creation']
        verbose_name = _("Favori")
        verbose_name_plural = _("Favoris")


class LikeCommentaire(models.Model):
    """Modèle pour gérer les likes des commentaires par les utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_commentaires', verbose_name=_("Utilisateur"))
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE, related_name='likes_commentaire', verbose_name=_("Commentaire"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de création"))
    
    def __str__(self):
        return f'{self.user.username} aime le commentaire de {self.commentaire.nom_auteur}'
    
    class Meta:
        unique_together = ('user', 'commentaire')  # Un utilisateur ne peut liker qu'une fois le même commentaire
        ordering = ['-date_creation']
        verbose_name = _("Like de commentaire")
        verbose_name_plural = _("Likes de commentaires")


class SignalementCommentaire(models.Model):
    """Modèle pour gérer les signalements de commentaires inappropriés"""
    MOTIFS = [
        ('spam', _('Spam')),
        ('harcelement', _('Harcèlement')),
        ('contenu_inapproprie', _('Contenu inapproprié')),
        ('fausses_informations', _('Fausses informations')),
        ('autre', _('Autre')),
    ]
    
    STATUTS = [
        ('en_attente', _('En attente')),
        ('traite', _('Traité')),
        ('rejete', _('Rejeté')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signalements', verbose_name=_("Utilisateur signalant"))
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE, related_name='signalements', verbose_name=_("Commentaire signalé"))
    motif = models.CharField(max_length=50, choices=MOTIFS, verbose_name=_("Motif"))
    description = models.TextField(blank=True, max_length=500, help_text=_('Description détaillée du problème (optionnel)'), verbose_name=_("Description"))
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente', verbose_name=_("Statut"))
    date_creation = models.DateTimeField(default=timezone.now, verbose_name=_("Date de signalement"))
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de traitement"))
    moderateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_traites', verbose_name=_("Modérateur"))
    
    def __str__(self):
        return f'Signalement de {self.user.username} pour le commentaire de {self.commentaire.nom_auteur}'
    
    def marquer_comme_traite(self, moderateur):
        """Marque le signalement comme traité"""
        self.statut = 'traite'
        self.date_traitement = timezone.now()
        self.moderateur = moderateur
        self.save()
    
    def marquer_comme_rejete(self, moderateur):
        """Marque le signalement comme rejeté"""
        self.statut = 'rejete'
        self.date_traitement = timezone.now()
        self.moderateur = moderateur
        self.save()
    
    class Meta:
        unique_together = ('user', 'commentaire')  # Un utilisateur ne peut signaler qu'une fois le même commentaire
        ordering = ['-date_creation']
        verbose_name = _("Signalement de commentaire")
        verbose_name_plural = _("Signalements de commentaires")