from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max, Q
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from .models import Article, Commentaire, Categorie, VueArticle, Profil
from .forms import ArticleForm, CommentaireForm, InscriptionForm, ConnexionForm, ProfilForm


def role_required(roles):
    """Décorateur pour vérifier les rôles des utilisateurs"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
                return redirect('connexion')
            
            if not hasattr(request.user, 'profil'):
                messages.error(request, 'Profil utilisateur non trouvé.')
                return redirect('home')
            
            if request.user.profil.role not in roles:
                messages.error(request, 'Vous n\'avez pas les permissions nécessaires pour accéder à cette page.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def inscription(request):
    """Vue d'inscription des utilisateurs"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé avec succès pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('connexion')
    else:
        form = InscriptionForm()
    
    return render(request, 'blog/inscription.html', {'form': form})


def connexion(request):
    """Vue de connexion des utilisateurs"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Mettre à jour la dernière connexion
            if hasattr(user, 'profil'):
                user.profil.derniere_connexion = timezone.now()
                user.profil.save()
            
            messages.success(request, f'Bienvenue {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = ConnexionForm()
    
    return render(request, 'blog/connexion.html', {'form': form})


def deconnexion(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')


@login_required
def profil(request):
    """Vue du profil utilisateur"""
    profil_user = request.user.profil
    
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=profil_user, user=request.user)
        if form.is_valid():
            # Sauvegarder les informations du profil
            profil_user = form.save()
            
            # Sauvegarder les informations de l'utilisateur
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('profil')
    else:
        form = ProfilForm(instance=profil_user, user=request.user)
    
    # Statistiques de l'utilisateur
    articles_utilisateur = Article.objects.filter(user_auteur=request.user)
    commentaires_utilisateur = Commentaire.objects.filter(user_auteur=request.user)
    
    stats = {
        'articles_publies': articles_utilisateur.filter(est_publie=True).count(),
        'articles_brouillons': articles_utilisateur.filter(est_publie=False).count(),
        'total_vues': sum(article.nombre_vues for article in articles_utilisateur),
        'commentaires_ecrits': commentaires_utilisateur.count(),
    }
    
    return render(request, 'blog/profil.html', {
        'form': form,
        'profil_user': profil_user,
        'stats': stats,
        'articles_recents': articles_utilisateur[:5]
    })


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


@role_required(['auteur', 'moderateur', 'admin'])
def ajouter_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user_auteur = request.user
            article.save()
            form.save_m2m()  # Pour sauvegarder les relations many-to-many (tags)
            
            if article.est_publie:
                messages.success(request, 'Article publié avec succès!')
            else:
                messages.success(request, 'Article sauvegardé en brouillon!')
            return redirect('detail_article', article_id=article.id)
    else:
        form = ArticleForm()

    return render(request, 'blog/ajouter_article.html', {'form': form})


def detail_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Vérifier si l'article est publié ou si l'utilisateur est l'auteur
    if not article.est_publie and (not request.user.is_authenticated or article.user_auteur != request.user):
        messages.error(request, 'Article non trouvé.')
        return redirect('home')
    
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
    
    # Filtrer les commentaires approuvés
    commentaires = article.commentaires.filter(est_approuve=True)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Vous devez être connecté pour commenter.')
            return redirect('connexion')
        
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.user_auteur = request.user
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


@login_required
def mes_articles(request):
    """Vue pour afficher les articles de l'utilisateur connecté"""
    articles_list = Article.objects.filter(user_auteur=request.user).order_by('-date_creation')
    
    return render(request, 'blog/mes_articles.html', {
        'articles': articles_list
    })


@role_required(['moderateur', 'admin'])
def moderation(request):
    """Vue de modération pour les modérateurs et admins"""
    commentaires_en_attente = Commentaire.objects.filter(est_approuve=False)
    articles_recents = Article.objects.all().order_by('-date_creation')[:10]
    
    return render(request, 'blog/moderation.html', {
        'commentaires_en_attente': commentaires_en_attente,
        'articles_recents': articles_recents
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