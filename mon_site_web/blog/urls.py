from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentification
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('profil/', views.profil_view, name='profil'),
    path('utilisateur/<str:username>/', views.profil_public_view, name='profil_public'),
    
    # Mot de passe oublié
    path('mot-de-passe-oublie/', views.MotDePasseOublieView.as_view(), name='mot_de_passe_oublie'),
    path('mot-de-passe-oublie/envoye/', views.MotDePasseOublieEnvoyeView.as_view(), name='mot_de_passe_oublie_envoye'),
    path('reset/<uidb64>/<token>/', views.NouveauMotDePasseView.as_view(), name='nouveau_mot_de_passe'),
    path('mot-de-passe-reinitialise/', views.MotDePasseReinitialiseView.as_view(), name='mot_de_passe_reinitialise'),
    
    # Articles
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/<int:article_id>/', views.detail_article, name='detail_article'),
    path('article/<int:article_id>/modifier/', views.modifier_article, name='modifier_article'),
    path('articles/', views.articles_view, name='articles'),
    path('mes-articles/', views.mes_articles_view, name='mes_articles'),
    
    # Modération
    path('moderation/', views.moderation_view, name='moderation'),
    path('moderation/approuver/<int:commentaire_id>/', views.approuver_commentaire, name='approuver_commentaire'),
    path('moderation/supprimer/<int:commentaire_id>/', views.supprimer_commentaire, name='supprimer_commentaire'),
    
    # Pages statiques
    path('categories/', views.categories_view, name='categories'),
    path('auteurs/', views.auteurs_view, name='auteurs'),
    path('a-propos/', views.a_propos_view, name='a_propos'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Likes et Bookmarks
    path('article/<int:article_id>/like/', views.toggle_like, name='toggle_like'),
    path('article/<int:article_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('commentaire/<int:commentaire_id>/like/', views.toggle_like_commentaire, name='toggle_like_commentaire'),
    path('mes-favoris/', views.mes_favoris_view, name='mes_favoris'),
    path('mes-likes/', views.mes_likes_view, name='mes_likes'),
    
    # Signalements
    path('commentaire/<int:commentaire_id>/signaler/', views.signaler_commentaire, name='signaler_commentaire'),
    path('moderation/signalements/', views.gerer_signalements, name='gerer_signalements'),
    path('moderation/signalement/<int:signalement_id>/traiter/', views.traiter_signalement, name='traiter_signalement'),
]