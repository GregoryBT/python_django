from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Max, Q
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from .models import Article, Commentaire, Categorie, VueArticle, Profil
from .forms import ArticleForm, CommentaireForm, InscriptionForm, ConnexionForm, ProfilForm


def home(request):
    """Vue de la page d'accueil avec fonctionnalité de recherche"""
    search_query = request.GET.get('search')
    articles = Article.objects.filter(est_publie=True).order_by('-date_creation')
    
    # Recherche par titre ou auteur
    if search_query:
        articles = articles.filter(
            Q(titre__icontains=search_query) | 
            Q(auteur__icontains=search_query)
        )
    
    # Calcul de la date d'il y a un mois
    un_mois_avant = timezone.now() - timedelta(days=30)
    
    # Articles les plus populaires (top 5 par nombre de vues)
    articles_populaires = Article.objects.filter(est_publie=True).order_by('-nombre_vues')[:5]
    
    # Activité récente (derniers articles et commentaires)
    activite_recente = []
    
    # Derniers articles (3 plus récents)
    derniers_articles = Article.objects.filter(est_publie=True).order_by('-date_creation')[:3]
    for article in derniers_articles:
        activite_recente.append({
            'description': f'Nouvel article: "{article.titre}" par {article.get_auteur_display()}',
            'date': article.date_creation,
            'icone': '📄',
            'couleur': 'blue'
        })
    
    # Derniers commentaires (3 plus récents)
    derniers_commentaires = Commentaire.objects.filter(est_approuve=True).order_by('-date_creation')[:3]
    for commentaire in derniers_commentaires:
        activite_recente.append({
            'description': f'{commentaire.get_nom_auteur()} a commenté "{commentaire.article.titre}"',
            'date': commentaire.date_creation,
            'icone': '💬',
            'couleur': 'green'
        })
    
    # Trier l'activité par date (plus récent en premier)
    activite_recente.sort(key=lambda x: x['date'], reverse=True)
    activite_recente = activite_recente[:6]  # Garder seulement les 6 plus récents
    
    # Statistiques pour la page d'accueil
    stats = {
        'total_articles': Article.objects.filter(est_publie=True).count(),
        'total_auteurs': Article.objects.filter(est_publie=True).values('user_auteur').distinct().count(),
        'lecteurs_ce_mois': sum(article.nombre_vues for article in Article.objects.filter(est_publie=True)),
        'total_commentaires': Commentaire.objects.filter(est_approuve=True).count(),
        'total_categories': Categorie.objects.count(),
        'articles_populaires': articles_populaires,
        'activite_recente': activite_recente,
    }
    
    return render(request, 'blog/home.html', {
        'articles': articles,
        'search_query': search_query,
        'stats': stats
    })


def inscription_view(request):
    """Vue d'inscription des utilisateurs"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('connexion')
    else:
        form = InscriptionForm()
    
    return render(request, 'blog/inscription.html', {'form': form})


def connexion_view(request):
    """Vue de connexion des utilisateurs"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Mettre à jour la dernière connexion dans le profil
                if hasattr(user, 'profil'):
                    user.profil.derniere_connexion = timezone.now()
                    user.profil.save()
                
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = ConnexionForm()
    
    return render(request, 'blog/connexion.html', {'form': form})


def deconnexion_view(request):
    """Vue de déconnexion"""
    if request.user.is_authenticated:
        messages.info(request, f'Au revoir {request.user.get_full_name() or request.user.username} !')
    logout(request)
    return redirect('home')


@login_required
def profil_view(request):
    """Vue du profil utilisateur"""
    profil_user = request.user.profil
    
    # Calculer les statistiques
    articles_user = Article.objects.filter(user_auteur=request.user)
    stats = {
        'articles_publies': articles_user.filter(est_publie=True).count(),
        'articles_brouillons': articles_user.filter(est_publie=False).count(),
        'total_vues': sum(article.nombre_vues for article in articles_user),
        'commentaires_ecrits': Commentaire.objects.filter(user_auteur=request.user).count(),
    }
    
    # Articles récents
    articles_recents = articles_user.order_by('-date_creation')[:5]
    
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user, profil_instance=profil_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user, profil_instance=profil_user)
    
    return render(request, 'blog/profil.html', {
        'form': form,
        'profil_user': profil_user,
        'stats': stats,
        'articles_recents': articles_recents,
    })


@login_required
def ajouter_article(request):
    """Vue pour ajouter un nouvel article"""
    if not request.user.profil.peut_creer_article():
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des articles.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user_auteur = request.user  # Assigner l'utilisateur connecté
            article.save()
            form.save_m2m()  # Sauvegarder les relations many-to-many (tags)
            messages.success(request, 'Article créé avec succès !')
            return redirect('detail_article', article_id=article.id)
    else:
        form = ArticleForm()
    
    return render(request, 'blog/ajouter_article.html', {'form': form})


def detail_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Vérifier si l'article est publié ou si l'utilisateur peut le voir
    if not article.est_publie:
        if not request.user.is_authenticated:
            messages.error(request, 'Cet article n\'est pas disponible.')
            return redirect('home')
        if article.user_auteur != request.user and not request.user.profil.peut_moderer():
            messages.error(request, 'Cet article n\'est pas disponible.')
            return redirect('home')
    
    # Tracker les vues uniquement pour les articles publiés
    if article.est_publie:
        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip

        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Éviter de compter plusieurs vues de la même IP dans la même heure
        une_heure_ago = timezone.now() - timedelta(hours=1)
        
        vue_recente = VueArticle.objects.filter(
            article=article,
            adresse_ip=client_ip,
            date_vue__gte=une_heure_ago
        ).exists()

        if not vue_recente:
            VueArticle.objects.create(
                article=article,
                adresse_ip=client_ip,
                user_agent=user_agent
            )
            article.incrementer_vues()
    
    # Commentaires approuvés
    commentaires = article.commentaires.filter(est_approuve=True).order_by('date_creation')
    
    # Formulaire de commentaire
    commentaire_form = None
    if request.method == 'POST' and 'commentaire' in request.POST:
        if request.user.is_authenticated:
            commentaire_form = CommentaireForm(request.POST)
            if commentaire_form.is_valid():
                commentaire = commentaire_form.save(commit=False)
                commentaire.article = article
                commentaire.user_auteur = request.user
                # Les commentaires des auteurs, modérateurs et admins sont automatiquement approuvés
                if request.user.profil.peut_creer_article():
                    commentaire.est_approuve = True
                commentaire.save()
                messages.success(request, 'Votre commentaire a été ajouté avec succès !')
                return redirect('detail_article', article_id=article.id)
        else:
            messages.error(request, 'Vous devez être connecté pour laisser un commentaire.')
    
    if not commentaire_form:
        commentaire_form = CommentaireForm()
    
    # Articles similaires (même catégorie)
    articles_similaires = Article.objects.filter(
        categorie=article.categorie,
        est_publie=True
    ).exclude(id=article.id)[:3]
    
    return render(request, 'blog/detail_article.html', {
        'article': article,
        'commentaires': commentaires,
        'commentaire_form': commentaire_form,
        'articles_similaires': articles_similaires,
    })


@login_required
def mes_articles_view(request):
    """Vue pour afficher les articles de l'utilisateur connecté"""
    if not request.user.profil.peut_creer_article():
        messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette page.')
        return redirect('home')
    
    articles = Article.objects.filter(user_auteur=request.user).order_by('-date_creation')
    
    # Calculer les statistiques
    stats = {
        'total_articles': articles.count(),
        'articles_publies': articles.filter(est_publie=True).count(),
        'articles_brouillons': articles.filter(est_publie=False).count(),
        'total_vues': sum(article.nombre_vues for article in articles),
    }
    
    return render(request, 'blog/mes_articles.html', {
        'articles': articles,
        'stats': stats,
    })


def peut_moderer(user):
    """Vérifie si l'utilisateur peut modérer"""
    return user.is_authenticated and user.profil.peut_moderer()


@user_passes_test(peut_moderer)
def moderation_view(request):
    """Vue de modération pour les modérateurs et admins"""
    # Commentaires en attente
    commentaires_en_attente = Commentaire.objects.filter(est_approuve=False).order_by('-date_creation')
    
    # Commentaires approuvés récents
    commentaires_approuves = Commentaire.objects.filter(est_approuve=True).order_by('-date_creation')[:10]
    
    # Articles récents
    articles_recents = Article.objects.order_by('-date_creation')[:10]
    
    # Statistiques pour les administrateurs
    stats_admin = {}
    if request.user.profil.est_admin():
        stats_admin = {
            'total_utilisateurs': User.objects.count(),
            'total_articles': Article.objects.filter(est_publie=True).count(),
            'total_commentaires': Commentaire.objects.filter(est_approuve=True).count(),
        }
    
    # Utilisateurs actifs (connectés dans les 7 derniers jours)
    date_limite = timezone.now() - timedelta(days=7)
    utilisateurs_actifs = User.objects.filter(
        profil__derniere_connexion__gte=date_limite
    ).count()
    
    return render(request, 'blog/moderation.html', {
        'commentaires_en_attente': commentaires_en_attente,
        'commentaires_approuves': commentaires_approuves,
        'articles_recents': articles_recents,
        'utilisateurs_actifs': utilisateurs_actifs,
        **stats_admin,
    })


@user_passes_test(peut_moderer)
def approuver_commentaire(request, commentaire_id):
    """Approuver un commentaire"""
    if request.method == 'POST':
        try:
            commentaire = Commentaire.objects.get(id=commentaire_id)
            commentaire.est_approuve = True
            commentaire.save()
            messages.success(request, 'Commentaire approuvé avec succès.')
        except Commentaire.DoesNotExist:
            messages.error(request, 'Commentaire introuvable.')
    
    return redirect('moderation')


@user_passes_test(peut_moderer)
def supprimer_commentaire(request, commentaire_id):
    """Supprimer un commentaire"""
    if request.method == 'POST':
        try:
            commentaire = Commentaire.objects.get(id=commentaire_id)
            commentaire.delete()
            messages.success(request, 'Commentaire supprimé avec succès.')
        except Commentaire.DoesNotExist:
            messages.error(request, 'Commentaire introuvable.')
    
    return redirect('moderation')


def articles_view(request):
    """Vue pour afficher tous les articles"""
    articles = Article.objects.filter(est_publie=True).order_by('-date_creation')
    
    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        articles = articles.filter(categorie_id=categorie_id)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        articles = articles.filter(
            Q(titre__icontains=search) |
            Q(contenu__icontains=search)
        )
    
    # Toutes les catégories pour le filtre
    categories = Categorie.objects.all()
    
    return render(request, 'blog/articles.html', {
        'articles': articles,
        'categories': categories,
        'search': search,
        'selected_category': categorie_id
    })


def categories_view(request):
    """Vue pour afficher toutes les catégories"""
    categories = Categorie.objects.annotate(
        nb_articles=Count('articles', filter=Q(articles__est_publie=True))
    ).filter(nb_articles__gt=0)
    
    return render(request, 'blog/categories.html', {
        'categories': categories
    })


def auteurs_view(request):
    """Vue pour afficher tous les auteurs"""
    auteurs = User.objects.filter(
        articles__est_publie=True
    ).annotate(
        nb_articles=Count('articles', filter=Q(articles__est_publie=True)),
        total_vues=Count('articles__vuearticle', filter=Q(articles__est_publie=True))
    ).distinct().order_by('-nb_articles')
    
    return render(request, 'blog/auteurs.html', {
        'auteurs': auteurs
    })


def a_propos_view(request):
    """Vue de la page À propos"""
    return render(request, 'blog/a_propos.html')