from django.contrib import admin
from .models import Article, Categorie, Commentaire, Tag, VueArticle

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'couleur', 'date_creation', 'nombre_articles')
    list_filter = ('date_creation',)
    search_fields = ('nom', 'description')
    readonly_fields = ('date_creation',)
    
    def nombre_articles(self, obj):
        return obj.articles.count()
    nombre_articles.short_description = 'Nombre d\'articles'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'categorie', 'date_creation', 'nombre_commentaires')
    list_filter = ('categorie', 'date_creation', 'auteur')
    search_fields = ('titre', 'contenu', 'auteur')
    readonly_fields = ('date_creation',)
    
    def nombre_commentaires(self, obj):
        return obj.commentaires.count()
    nombre_commentaires.short_description = 'Commentaires'

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('nom_auteur', 'article', 'date_creation', 'contenu_court')
    list_filter = ('date_creation', 'article')
    search_fields = ('nom_auteur', 'contenu', 'article__titre')
    readonly_fields = ('date_creation',)
    
    def contenu_court(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    contenu_court.short_description = 'Contenu'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'couleur', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}
