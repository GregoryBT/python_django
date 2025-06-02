from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Max
from .models import Article, Commentaire, Categorie
from .forms import ArticleForm, CommentaireForm


def home(request):
    categorie_id = request.GET.get('categorie')
    articles = Article.objects.all()
    
    if categorie_id:
        articles = articles.filter(categorie_id=categorie_id)
    
    # Grouper les articles par catégorie
    categories = Categorie.objects.all()
    articles_par_categorie = {}
    articles_sans_categorie = articles.filter(categorie__isnull=True)
    
    for categorie in categories:
        articles_categorie = articles.filter(categorie=categorie)
        if articles_categorie:
            articles_par_categorie[categorie] = articles_categorie
    
    return render(request, 'blog/home.html', {
        'articles': articles,
        'categories': categories,
        'articles_par_categorie': articles_par_categorie,
        'articles_sans_categorie': articles_sans_categorie,
        'categorie_selectionnee': categorie_id
    })


def ajouter_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article ajouté avec succès!')
            return redirect('home')
    else:
        form = ArticleForm()

    return render(request, 'blog/ajouter_article.html', {'form': form})


def detail_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
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