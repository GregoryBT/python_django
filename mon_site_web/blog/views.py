from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
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