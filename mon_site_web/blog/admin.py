from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Article, Commentaire, Categorie, Tag, VueArticle, Profil, Like, Bookmark

# Inline pour afficher le profil dans l'admin des utilisateurs
class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['role', 'bio', 'avatar', 'site_web']

# Étendre l'admin des utilisateurs
class CustomUserAdmin(UserAdmin):
    inlines = (ProfilInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'profil__role']
    
    def get_role(self, obj):
        return obj.profil.get_role_display() if hasattr(obj, 'profil') else 'Aucun profil'
    get_role.short_description = 'Rôle'

# Réenregistrer l'admin des utilisateurs
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'date_creation', 'derniere_connexion']
    list_filter = ['role', 'date_creation']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['date_creation']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'role')
        }),
        ('Informations personnelles', {
            'fields': ('bio', 'avatar', 'site_web')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'derniere_connexion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur', 'nb_articles', 'date_creation']
    search_fields = ['nom', 'description']
    readonly_fields = ['date_creation']
    
    def nb_articles(self, obj):
        return obj.articles.count()
    nb_articles.short_description = 'Nombre d\'articles'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'couleur', 'nb_articles', 'date_creation']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}
    readonly_fields = ['date_creation']
    
    def nb_articles(self, obj):
        return obj.articles.count()
    nb_articles.short_description = 'Nombre d\'articles'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'get_auteur', 'categorie', 'est_publie', 'nombre_vues', 'date_creation']
    list_filter = ['est_publie', 'categorie', 'date_creation', 'user_auteur__profil__role']
    search_fields = ['titre', 'contenu', 'auteur', 'user_auteur__username']
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ['nombre_vues', 'date_creation']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('titre', 'slug', 'contenu', 'image')
        }),
        ('Métadonnées', {
            'fields': ('auteur', 'user_auteur', 'categorie', 'tags', 'est_publie')
        }),
        ('Statistiques', {
            'fields': ('nombre_vues', 'date_creation'),
            'classes': ('collapse',)
        }),
    )
    
    def get_auteur(self, obj):
        if obj.user_auteur:
            return f"{obj.user_auteur.get_full_name() or obj.user_auteur.username} ({obj.user_auteur.profil.get_role_display()})"
        return obj.auteur
    get_auteur.short_description = 'Auteur'
    
    def save_model(self, request, obj, form, change):
        # Si pas d'auteur utilisateur défini, utiliser l'utilisateur actuel
        if not obj.user_auteur and hasattr(request.user, 'profil') and request.user.profil.peut_creer_article():
            obj.user_auteur = request.user
        super().save_model(request, obj, form, change)

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['get_auteur', 'article', 'contenu_court', 'est_approuve', 'date_creation']
    list_filter = ['est_approuve', 'date_creation', 'user_auteur__profil__role']
    search_fields = ['contenu', 'nom_auteur', 'user_auteur__username', 'article__titre']
    readonly_fields = ['date_creation']
    actions = ['approuver_commentaires', 'desapprouver_commentaires']
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('article', 'contenu')
        }),
        ('Auteur', {
            'fields': ('nom_auteur', 'user_auteur')
        }),
        ('Modération', {
            'fields': ('est_approuve', 'date_creation')
        }),
    )
    
    def get_auteur(self, obj):
        if obj.user_auteur:
            return f"{obj.user_auteur.get_full_name() or obj.user_auteur.username} ({obj.user_auteur.profil.get_role_display()})"
        return obj.nom_auteur
    get_auteur.short_description = 'Auteur'
    
    def contenu_court(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    contenu_court.short_description = 'Contenu'
    
    def approuver_commentaires(self, request, queryset):
        updated = queryset.update(est_approuve=True)
        self.message_user(request, f'{updated} commentaire(s) approuvé(s).')
    approuver_commentaires.short_description = 'Approuver les commentaires sélectionnés'
    
    def desapprouver_commentaires(self, request, queryset):
        updated = queryset.update(est_approuve=False)
        self.message_user(request, f'{updated} commentaire(s) désapprouvé(s).')
    desapprouver_commentaires.short_description = 'Désapprouver les commentaires sélectionnés'

@admin.register(VueArticle)
class VueArticleAdmin(admin.ModelAdmin):
    list_display = ['article', 'adresse_ip', 'date_vue']
    list_filter = ['date_vue']
    search_fields = ['article__titre', 'adresse_ip']
    readonly_fields = ['article', 'adresse_ip', 'user_agent', 'date_vue']
    
    def has_add_permission(self, request):
        return False  # Empêcher l'ajout manuel de vues

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['user__username', 'article__titre']
    readonly_fields = ['date_creation']
    
    def has_add_permission(self, request):
        return False  # Les likes se font via l'interface utilisateur

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'date_creation', 'has_note']
    list_filter = ['date_creation']
    search_fields = ['user__username', 'article__titre', 'note_personnelle']
    readonly_fields = ['date_creation']
    
    fieldsets = (
        ('Favori', {
            'fields': ('user', 'article', 'date_creation')
        }),
        ('Note personnelle', {
            'fields': ('note_personnelle',),
            'classes': ('collapse',)
        }),
    )
    
    def has_note(self, obj):
        return bool(obj.note_personnelle)
    has_note.boolean = True
    has_note.short_description = 'A une note'
    
    def has_add_permission(self, request):
        return False  # Les favoris se font via l'interface utilisateur

# Configuration du site admin
admin.site.site_header = "Administration - Blog Académique Universitaire"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Gestion du Blog"
