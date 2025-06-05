from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.db.models import Count, Max, Q, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from django.core.paginator import Paginator
from .models import Article, Commentaire, Categorie, VueArticle, Profil, Like, Bookmark, LikeCommentaire, SignalementCommentaire
from .forms import ArticleForm, CommentaireForm, InscriptionForm, ConnexionForm, ProfilForm, MotDePasseOublieForm, NouveauMotDePasseForm, SignalementCommentaireForm
from .services import GeminiService, DalleService
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json


def home(request):
    """Vue de la page d'accueil avec fonctionnalité de recherche et pagination"""
    search_query = request.GET.get('search')
    articles = Article.objects.filter(est_publie=True).order_by('-date_creation')
    
    # Recherche par titre ou auteur
    if search_query:
        articles = articles.filter(
            Q(titre__icontains=search_query) | 
            Q(auteur__icontains=search_query)
        )
    
    # Pagination - 6 articles par page
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
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
        'articles': page_obj,  # Utiliser l'objet page au lieu de articles
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
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Mettre à jour la dernière connexion dans le profil
            if hasattr(user, 'profil'):
                user.profil.derniere_connexion = timezone.now()
                user.profil.save()
            
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
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
        form = ProfilForm(request.POST, request.FILES, profil_instance=profil_user, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('profil')
    else:
        form = ProfilForm(profil_instance=profil_user, instance=request.user)
    
    return render(request, 'blog/profil.html', {
        'form': form,
        'profil_user': profil_user,
        'stats': stats,
        'articles_recents': articles_recents,
    })


@login_required
def modifier_article(request, article_id):
    """Vue pour modifier un article existant"""
    article = get_object_or_404(Article, id=article_id)
    
    # Vérifier que l'utilisateur peut modifier cet article
    if not request.user.profil.peut_modifier_article(article):
        messages.error(request, 'Vous n\'avez pas les permissions pour modifier cet article.')
        return redirect('detail_article', article_id=article.id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            try:
                article = form.save(commit=False)
                # S'assurer que l'auteur reste le même
                if not article.user_auteur:
                    article.user_auteur = request.user
                article.save()
                form.save_m2m()  # Sauvegarder les relations many-to-many (tags)
                messages.success(request, 'Article modifié avec succès !')
                return redirect('detail_article', article_id=article.id)
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification de l\'article : {str(e)}')
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans le champ {field}: {error}')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'blog/modifier_article.html', {
        'form': form,
        'article': article
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
            try:
                article = form.save(commit=False)
                article.user_auteur = request.user  # Assigner l'utilisateur connecté
                
                # Gérer l'image temporaire générée par DALL-E si elle existe
                temp_image_path = request.POST.get('temp_image_path')
                if temp_image_path and not article.image:
                    try:
                        from django.core.files.storage import default_storage
                        from django.core.files.base import ContentFile
                        
                        if default_storage.exists(temp_image_path):
                            # Lire l'image temporaire
                            with default_storage.open(temp_image_path, 'rb') as temp_file:
                                image_content = temp_file.read()
                            
                            # Créer un nom de fichier pour l'article
                            import os
                            filename = os.path.basename(temp_image_path).replace('temp_dalle_', 'article_')
                            
                            # Sauvegarder l'image dans le champ image de l'article
                            article.image.save(filename, ContentFile(image_content), save=False)
                            
                            # Supprimer l'image temporaire
                            default_storage.delete(temp_image_path)
                    except Exception as e:
                        print(f"Erreur lors de l'application de l'image temporaire: {str(e)}")
                        # Continuer sans image si erreur
                
                article.save()
                form.save_m2m()  # Sauvegarder les relations many-to-many (tags)
                messages.success(request, 'Article créé avec succès !')
                return redirect('detail_article', article_id=article.id)
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de l\'article : {str(e)}')
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans le champ {field}: {error}')
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
    
    # Ajouter les informations de permissions à l'article pour l'utilisateur connecté
    if request.user.is_authenticated:
        article.peut_modifier = request.user.profil.peut_modifier_article(article)
        article.peut_supprimer = request.user.profil.peut_supprimer_article(article)
        article.est_like = article.est_like_par_user(request.user)
    else:
        article.peut_modifier = False
        article.peut_supprimer = False
        article.est_like = False
    
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

        # Éviter de compter plusieurs vues de la même IP dans les 5 dernières minutes (au lieu d'1 heure)
        cinq_minutes_ago = timezone.now() - timedelta(minutes=5)
        
        vue_recente = VueArticle.objects.filter(
            article=article,
            adresse_ip=client_ip,
            date_vue__gte=cinq_minutes_ago
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
    
    # Ajouter l'information des likes aux commentaires pour l'utilisateur connecté
    if request.user.is_authenticated:
        for commentaire in commentaires:
            commentaire.est_like_par_utilisateur_actuel = commentaire.est_like_par_user(request.user)
    else:
        for commentaire in commentaires:
            commentaire.est_like_par_utilisateur_actuel = False
    
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
    
    # Ajouter les informations de permissions à chaque article
    for article in articles:
        article.peut_modifier = request.user.profil.peut_modifier_article(article)
        article.peut_supprimer = request.user.profil.peut_supprimer_article(article)
    
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
    
    # Signalements en attente
    signalements = SignalementCommentaire.objects.filter(statut='en_attente').order_by('-date_creation')
    
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
        'signalements': signalements,
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
    articles = Article.objects.filter(est_publie=True)
    
    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    categorie_selectionnee = None
    if categorie_id:
        articles = articles.filter(categorie_id=categorie_id)
        categorie_selectionnee = categorie_id
    
    # Tri
    sort_param = request.GET.get('sort', '-date_creation')
    sort_actuel = sort_param
    articles = articles.order_by(sort_param)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        articles = articles.filter(
            Q(titre__icontains=search) |
            Q(contenu__icontains=search)
        )
    
    # Ajouter l'information de like pour l'utilisateur connecté
    if request.user.is_authenticated:
        for article in articles:
            article.est_like = article.est_like_par_user(request.user)
    else:
        for article in articles:
            article.est_like = False
    
    # Toutes les catégories pour le filtre
    categories = Categorie.objects.all()
    
    return render(request, 'blog/articles.html', {
        'articles': articles,
        'categories': categories,
        'categorie_selectionnee': categorie_selectionnee,
        'sort_actuel': sort_actuel,
        'search': search,
    })


def categories_view(request):
    """Vue pour afficher toutes les catégories"""
    # Récupérer toutes les catégories avec le nombre d'articles publiés
    categories = Categorie.objects.annotate(
        nb_articles=Count('articles', filter=Q(articles__est_publie=True))
    ).order_by('-nb_articles', 'nom')
    
    # Compter les articles sans catégorie
    articles_sans_categorie = Article.objects.filter(
        categorie__isnull=True, 
        est_publie=True
    ).count()
    
    return render(request, 'blog/categories.html', {
        'categories': categories,
        'articles_sans_categorie': articles_sans_categorie
    })


def auteurs_view(request):
    """Vue pour afficher tous les auteurs"""
    auteurs = User.objects.filter(
        articles__est_publie=True
    ).annotate(
        nb_articles=Count('articles', filter=Q(articles__est_publie=True)),
        total_vues=Sum('articles__nombre_vues', filter=Q(articles__est_publie=True))
    ).distinct().order_by('-nb_articles')
    
    return render(request, 'blog/auteurs.html', {
        'auteurs': auteurs
    })


def a_propos_view(request):
    """Vue de la page À propos"""
    return render(request, 'blog/a_propos.html')


@user_passes_test(peut_moderer)
def analytics_view(request):
    """Vue d'analytics pour les administrateurs"""
    # Statistiques générales
    stats = {
        'total_articles': Article.objects.filter(est_publie=True).count(),
        'total_auteurs': User.objects.filter(profil__role='administrateur').count() + User.objects.filter(articles__est_publie=True).distinct().count(),
        'total_vues': sum(article.nombre_vues for article in Article.objects.filter(est_publie=True)),
        'moyenne_vues_par_article': Article.objects.filter(est_publie=True).aggregate(Avg('nombre_vues'))['nombre_vues__avg'] or 0,
        'total_commentaires': Commentaire.objects.filter(est_approuve=True).count(),
    }
    
    # Articles les plus populaires
    articles_populaires = Article.objects.filter(est_publie=True).order_by('-nombre_vues')[:10]
    
    # Auteurs les plus actifs
    auteurs_actifs = User.objects.filter(
        articles__est_publie=True
    ).annotate(
        nb_articles=Count('articles', filter=Q(articles__est_publie=True)),
        total_vues=Sum('articles__nombre_vues', filter=Q(articles__est_publie=True))
    ).order_by('-nb_articles')[:10]
    
    # Évolution des vues par mois (6 derniers mois)
    six_mois_avant = timezone.now() - timedelta(days=180)
    vues_par_mois = VueArticle.objects.filter(
        date_vue__gte=six_mois_avant
    ).extra({
        'mois': "DATE_FORMAT(date_vue, '%%Y-%%m')"
    }).values('mois').annotate(
        total_vues=Count('id')
    ).order_by('mois')
    
    return render(request, 'blog/analytics.html', {
        'stats': stats,
        'articles_populaires': articles_populaires,
        'auteurs_actifs': auteurs_actifs,
        'vues_par_mois': vues_par_mois,
    })


def envoyer_notification_email(destinataire, sujet, message):
    """Envoie une notification par email"""
    try:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [destinataire],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email: {e}")


@login_required
def ajouter_commentaire(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            commentaire.save()
            
            # Notification email to article author
            if article.auteur.email:
                sujet = f"Nouveau commentaire sur votre article: {article.titre}"
                message = f"""
Bonjour {article.auteur.username},

Vous avez reçu un nouveau commentaire sur votre article "{article.titre}".

Commentaire de {request.user.username}:
{commentaire.contenu}

Consultez votre article: http://localhost:8000/article/{article.id}/
                """
                envoyer_notification_email(article.auteur.email, sujet, message)
            
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('detail_article', article_id=article.id)
    else:
        form = CommentaireForm()
    
    return render(request, 'blog/detail_article.html', {
        'article': article,
        'form': form
    })


class MotDePasseOublieView(PasswordResetView):
    """Vue pour la demande de réinitialisation de mot de passe"""
    template_name = 'blog/mot_de_passe_oublie.html'
    email_template_name = 'blog/mot_de_passe_oublie_email.html'
    subject_template_name = 'blog/mot_de_passe_oublie_sujet.txt'
    form_class = MotDePasseOublieForm
    success_url = reverse_lazy('mot_de_passe_oublie_envoye')
    
    def form_valid(self, form):
        messages.success(self.request, 'Un email avec les instructions pour réinitialiser votre mot de passe a été envoyé.')
        return super().form_valid(form)


class MotDePasseOublieEnvoyeView(PasswordResetDoneView):
    """Vue après envoi de l'email de réinitialisation"""
    template_name = 'blog/mot_de_passe_oublie_envoye.html'


class NouveauMotDePasseView(PasswordResetConfirmView):
    """Vue pour définir un nouveau mot de passe"""
    template_name = 'blog/nouveau_mot_de_passe.html'
    form_class = NouveauMotDePasseForm
    success_url = reverse_lazy('mot_de_passe_reinitialise')
    
    def form_valid(self, form):
        messages.success(self.request, 'Votre mot de passe a été réinitialisé avec succès ! Vous pouvez maintenant vous connecter.')
        return super().form_valid(form)


class MotDePasseReinitialiseView(PasswordResetCompleteView):
    """Vue de confirmation après réinitialisation réussie"""
    template_name = 'blog/mot_de_passe_reinitialise.html'


@login_required
def toggle_like(request, article_id):
    """Vue pour liker/unliker un article via AJAX"""
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id, est_publie=True)
        like, created = Like.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            # Si le like existe déjà, on le supprime (unlike)
            like.delete()
            liked = False
            message = "Article retiré de vos favoris"
        else:
            # Nouveau like
            liked = True
            message = "Article ajouté à vos favoris"
        
        # Compter le nombre total de likes pour cet article
        total_likes = article.likes.count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Réponse AJAX
            from django.http import JsonResponse
            return JsonResponse({
                'liked': liked,
                'total_likes': total_likes,
                'message': message
            })
        
        messages.success(request, message)
        return redirect('detail_article', article_id=article.id)
    
    return redirect('detail_article', article_id=article_id)


@login_required
def toggle_bookmark(request, article_id):
    """Vue pour bookmarker/unbookmarker un article"""
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id, est_publie=True)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            # Si le bookmark existe déjà, on le supprime
            bookmark.delete()
            bookmarked = False
            message = "Article retiré de vos favoris"
        else:
            # Nouveau bookmark
            bookmarked = True
            message = "Article ajouté à vos favoris"
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Réponse AJAX
            from django.http import JsonResponse
            return JsonResponse({
                'bookmarked': bookmarked,
                'message': message
            })
        
        messages.success(request, message)
        return redirect('detail_article', article_id=article.id)
    
    return redirect('detail_article', article_id=article_id)


@login_required
def mes_favoris_view(request):
    """Vue pour afficher les articles mis en favoris par l'utilisateur"""
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-date_creation')
    
    # Pagination si nécessaire
    paginator = Paginator(bookmarks, 12)  # 12 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/mes_favoris.html', {
        'bookmarks': page_obj,
        'total_favoris': bookmarks.count()
    })


@login_required
def mes_likes_view(request):
    """Vue pour afficher les articles likés par l'utilisateur"""
    likes = Like.objects.filter(user=request.user).order_by('-date_creation')
    
    # Pagination si nécessaire
    paginator = Paginator(likes, 12)  # 12 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/mes_likes.html', {
        'likes': page_obj,
        'total_likes': likes.count()
    })


@login_required
def toggle_like_commentaire(request, commentaire_id):
    """Vue pour liker/unliker un commentaire via AJAX"""
    if request.method == 'POST':
        commentaire = get_object_or_404(Commentaire, id=commentaire_id, est_approuve=True)
        like, created = LikeCommentaire.objects.get_or_create(
            user=request.user,
            commentaire=commentaire
        )
        
        if not created:
            # Si le like existe déjà, on le supprime (unlike)
            like.delete()
            liked = False
            message = "Like retiré du commentaire"
        else:
            # Nouveau like
            liked = True
            message = "Commentaire liké"
        
        # Compter le nombre total de likes pour ce commentaire
        total_likes = commentaire.nombre_likes()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Réponse AJAX
            return JsonResponse({
                'liked': liked,
                'total_likes': total_likes,
                'message': message
            })
        
        messages.success(request, message)
        return redirect('detail_article', article_id=commentaire.article.id)
    
    return redirect('home')


@login_required
def signaler_commentaire(request, commentaire_id):
    """Vue pour signaler un commentaire inapproprié"""
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, est_approuve=True)
    
    # Vérifier si l'utilisateur a déjà signalé ce commentaire
    signalement_existant = SignalementCommentaire.objects.filter(
        user=request.user,
        commentaire=commentaire
    ).exists()
    
    if signalement_existant:
        messages.warning(request, 'Vous avez déjà signalé ce commentaire.')
        return redirect('detail_article', article_id=commentaire.article.id)
    
    if request.method == 'POST':
        form = SignalementCommentaireForm(request.POST)
        if form.is_valid():
            signalement = form.save(commit=False)
            signalement.user = request.user
            signalement.commentaire = commentaire
            signalement.save()
            
            # Notification aux modérateurs (optionnel)
            moderateurs = User.objects.filter(profil__role='administrateur')
            for moderateur in moderateurs:
                if moderateur.email:
                    sujet = f"Nouveau signalement de commentaire - {commentaire.article.titre}"
                    message = f"""
Bonjour {moderateur.get_full_name() or moderateur.username},

Un commentaire a été signalé sur l'article "{commentaire.article.titre}".

Signalé par : {request.user.get_full_name() or request.user.username}
Motif : {signalement.get_motif_display()}
Description : {signalement.description}

Commentaire signalé :
"{commentaire.contenu}"

Auteur du commentaire : {commentaire.get_nom_auteur()}

Veuillez vérifier ce signalement dans l'interface de modération.
                    """
                    envoyer_notification_email(moderateur.email, sujet, message)
            
            messages.success(request, 'Le commentaire a été signalé. Les modérateurs vont examiner votre signalement.')
            return redirect('detail_article', article_id=commentaire.article.id)
        else:
            messages.error(request, 'Erreur dans le formulaire de signalement.')
    else:
        form = SignalementCommentaireForm()
    
    return render(request, 'blog/signaler_commentaire.html', {
        'form': form,
        'commentaire': commentaire
    })


@user_passes_test(peut_moderer)
def gerer_signalements(request):
    """Vue pour gérer les signalements de commentaires (modérateurs uniquement)"""
    signalements_en_attente = SignalementCommentaire.objects.filter(
        statut='en_attente'
    ).order_by('-date_creation')
    
    signalements_traites = SignalementCommentaire.objects.filter(
        statut__in=['traite', 'rejete']
    ).order_by('-date_traitement')[:20]  # Les 20 derniers traités
    
    return render(request, 'blog/gerer_signalements.html', {
        'signalements_en_attente': signalements_en_attente,
        'signalements_traites': signalements_traites
    })


@user_passes_test(peut_moderer)
def traiter_signalement(request, signalement_id):
    """Vue pour traiter un signalement (approuver/rejeter)"""
    if request.method == 'POST':
        signalement = get_object_or_404(SignalementCommentaire, id=signalement_id)
        action = request.POST.get('action')
        
        if action == 'traiter':
            # Marquer comme traité et supprimer le commentaire
            signalement.marquer_comme_traite(request.user)
            signalement.commentaire.delete()
            messages.success(request, 'Signalement traité : le commentaire a été supprimé.')
        elif action == 'rejeter':
            # Marquer comme rejeté mais garder le commentaire
            signalement.marquer_comme_rejete(request.user)
            messages.success(request, 'Signalement rejeté : le commentaire reste visible.')
        
        return redirect('gerer_signalements')
    
    return redirect('gerer_signalements')


def profil_public_view(request, username):
    """Vue du profil public d'un utilisateur"""
    user = get_object_or_404(User, username=username)
    profil_user = user.profil
    
    # Calculer les statistiques publiques
    articles_user = Article.objects.filter(user_auteur=user, est_publie=True)
    stats = {
        'articles_publies': articles_user.count(),
        'total_vues': sum(article.nombre_vues for article in articles_user),
        'commentaires_ecrits': Commentaire.objects.filter(user_auteur=user, est_approuve=True).count(),
        'membre_depuis': user.date_joined,
    }
    
    # Articles récents (seulement les publiés)
    articles_recents = articles_user.order_by('-date_creation')[:6]
    
    # Articles les plus populaires de cet auteur
    articles_populaires = articles_user.order_by('-nombre_vues')[:3]
    
    return render(request, 'blog/profil_public.html', {
        'profil_user': profil_user,
        'user_profile': user,
        'stats': stats,
        'articles_recents': articles_recents,
        'articles_populaires': articles_populaires,
        'est_mon_profil': request.user == user,
    })


@login_required
def supprimer_article(request, article_id):
    """Vue pour supprimer un article existant"""
    article = get_object_or_404(Article, id=article_id)
    
    # Vérifier que l'utilisateur peut supprimer cet article
    if not request.user.profil.peut_supprimer_article(article):
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer cet article.')
        return redirect('detail_article', article_id=article.id)
    
    if request.method == 'POST':
        titre_article = article.titre
        article.delete()
        messages.success(request, f'L\'article "{titre_article}" a été supprimé avec succès.')
        return redirect('mes_articles')
    
    return render(request, 'blog/confirmer_suppression_article.html', {
        'article': article
    })


@login_required
@require_http_methods(["POST"])
def generer_avec_gemini(request):
    """Vue AJAX pour générer un article avec Gemini"""
    try:
        # Vérifier que l'utilisateur peut créer des articles
        if not request.user.profil.peut_creer_article():
            return JsonResponse({
                'success': False,
                'error': 'Vous n\'avez pas les permissions pour créer des articles.'
            }, status=403)
        
        # Récupérer le sujet depuis la requête
        data = json.loads(request.body)
        sujet = data.get('sujet', '').strip()
        generer_image = data.get('generer_image', False)
        
        if not sujet:
            return JsonResponse({
                'success': False,
                'error': 'Veuillez fournir un sujet pour générer l\'article.'
            }, status=400)
        
        if len(sujet) < 3:
            return JsonResponse({
                'success': False,
                'error': 'Le sujet doit contenir au moins 3 caractères.'
            }, status=400)
        
        # Initialiser le service Gemini
        gemini_service = GeminiService()
        
        if not gemini_service.is_available():
            return JsonResponse({
                'success': False,
                'error': 'Le service Gemini n\'est pas configuré. Veuillez contacter l\'administrateur.'
            }, status=500)
        
        # Générer l'article avec Gemini
        try:
            article_data = gemini_service.generer_article(sujet)
            
            # Générer une image avec DALL-E si demandé
            temp_image_path = None
            if generer_image:
                try:
                    dalle_service = DalleService()
                    if dalle_service.is_available():
                        # Utiliser le titre généré par Gemini pour créer l'image
                        image_file, temp_path = dalle_service.generer_image(article_data['titre'])
                        temp_image_path = temp_path
                    else:
                        # Service DALL-E non disponible, continuer sans image
                        pass
                except Exception as dalle_error:
                    # En cas d'erreur avec DALL-E, continuer sans image mais log l'erreur
                    print(f"Erreur lors de la génération d'image DALL-E: {str(dalle_error)}")
            
            # Préparer la réponse avec les données générées
            response_data = {
                'success': True,
                'data': {
                    'titre': article_data['titre'],
                    'contenu': article_data['contenu'],
                    'categorie_id': article_data['categorie'].id if article_data['categorie'] else None,
                    'categorie_nom': article_data['categorie'].nom if article_data['categorie'] else None,
                    'tags': [{'id': tag.id, 'nom': tag.nom} for tag in article_data['tags']],
                    'sujet_original': article_data['sujet_original'],
                    'image_generee': temp_image_path is not None,
                    'temp_image_path': temp_image_path
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de la génération de l\'article : {str(e)}'
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format de données invalide.'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur inattendue : {str(e)}'
        }, status=500)


@login_required
def recuperer_image_temporaire(request, temp_path):
    """Vue pour récupérer une image temporaire générée par DALL-E"""
    try:
        from django.core.files.storage import default_storage
        from django.http import HttpResponse
        
        if default_storage.exists(temp_path):
            with default_storage.open(temp_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="{temp_path.split("/")[-1]}"'
                return response
        else:
            return JsonResponse({'error': 'Image temporaire introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)