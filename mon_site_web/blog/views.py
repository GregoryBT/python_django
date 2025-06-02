from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Max, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Article, Commentaire, Categorie, VueArticle
from .forms import ArticleForm, CommentaireForm


def home(request):
    """Vue de la page d'accueil avec fonctionnalité de recherche"""
    search_query = request.GET.get('search')
    articles = Article.objects.all().order_by('-date_creation')
    
    # Recherche par titre ou auteur
    if search_query:
        articles = articles.filter(
            Q(titre__icontains=search_query) | 
            Q(auteur__icontains=search_query)
        )
    
    # Calcul de la date d'il y a un mois
    un_mois_avant = timezone.now() - timedelta(days=30)
    
    # Articles les plus populaires (top 5 par nombre de vues)
    articles_populaires = Article.objects.all().order_by('-nombre_vues')[:5]
    
    # Activité récente (derniers articles et commentaires)
    activite_recente = []
    
    # Derniers articles (3 plus récents)
    derniers_articles = Article.objects.all().order_by('-date_creation')[:3]
    for article in derniers_articles:
        activite_recente.append({
            'description': f'Nouvel article: "{article.titre}" par {article.auteur}',
            'date': article.date_creation,
            'icone': '📄',
            'couleur': 'blue'
        })
    
    # Derniers commentaires (3 plus récents)
    derniers_commentaires = Commentaire.objects.all().order_by('-date_creation')[:3]
    for commentaire in derniers_commentaires:
        activite_recente.append({
            'description': f'{commentaire.nom_auteur} a commenté "{commentaire.article.titre}"',
            'date': commentaire.date_creation,
            'icone': '💬',
            'couleur': 'green'
        })
    
    # Trier l'activité par date (plus récent en premier)
    activite_recente.sort(key=lambda x: x['date'], reverse=True)
    activite_recente = activite_recente[:6]  # Garder seulement les 6 plus récents
    
    # Statistiques pour la page d'accueil
    stats = {
        'total_articles': Article.objects.count(),
        'total_auteurs': Article.objects.values('auteur').distinct().count(),
        'lecteurs_ce_mois': sum(article.nombre_vues for article in Article.objects.all()),  # Toutes les vues, tous rafraîchissements inclus
        'total_commentaires': Commentaire.objects.count(),
        'total_categories': Categorie.objects.count(),
        'articles_populaires': articles_populaires,
        'activite_recente': activite_recente,
    }
    
    return render(request, 'blog/home.html', {
        'articles': articles,
        'search_query': search_query,
        'stats': stats
    })


def ajouter_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article ajouté avec succès!')
            return redirect('home')
    else:
        form = ArticleForm()

    return render(request, 'blog/ajouter_article.html', {'form': form})


def detail_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Incrémenter le nombre de vues à chaque visite (tous rafraîchissements inclus)
    article.nombre_vues += 1
    article.save()
    
    # Récupérer l'IP du visiteur
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    ip_address = get_client_ip(request)
    
    # Enregistrer la vue (pour des statistiques détaillées si nécessaire)
    VueArticle.objects.create(
        article=article,
        adresse_ip=ip_address,
        date_vue=timezone.now()
    )
    
    commentaires = article.commentaires.all()
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.save()
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('detail_article', article_id=article.id)
    else:
        form = CommentaireForm()
    
    return render(request, 'blog/detail_article.html', {
        'article': article,
        'commentaires': commentaires,
        'form': form
    })


def articles(request):
    """Vue pour afficher tous les articles avec pagination et tri"""
    articles_list = Article.objects.all().order_by('-date_creation')
    
    # Filtre par catégorie si demandé
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        articles_list = articles_list.filter(categorie_id=categorie_id)
    
    # Tri si demandé
    sort_by = request.GET.get('sort', '-date_creation')
    if sort_by in ['date_creation', '-date_creation', 'titre', '-titre']:
        articles_list = articles_list.order_by(sort_by)
    
    categories = Categorie.objects.all()
    
    return render(request, 'blog/articles.html', {
        'articles': articles_list,
        'categories': categories,
        'categorie_selectionnee': categorie_id,
        'sort_actuel': sort_by
    })


def categories(request):
    """Vue pour afficher toutes les catégories avec leurs statistiques"""
    categories_list = Categorie.objects.annotate(
        nb_articles=Count('articles')
    ).order_by('-nb_articles')
    
    return render(request, 'blog/categories.html', {
        'categories': categories_list
    })


def auteurs(request):
    """Vue pour afficher tous les auteurs avec leurs statistiques"""
    # Récupérer tous les auteurs uniques avec le nombre d'articles
    auteurs_list = Article.objects.values('auteur').annotate(
        nb_articles=Count('id'),
        dernier_article=Max('date_creation')
    ).order_by('-nb_articles')
    
    return render(request, 'blog/auteurs.html', {
        'auteurs': auteurs_list
    })


def a_propos(request):
    """Vue pour la page À propos"""
    # Statistiques du blog
    stats = {
        'total_articles': Article.objects.count(),
        'total_commentaires': Commentaire.objects.count(),
        'total_categories': Categorie.objects.count(),
        'total_auteurs': Article.objects.values('auteur').distinct().count(),
    }
    
    return render(request, 'blog/a_propos.html', {
        'stats': stats
    })