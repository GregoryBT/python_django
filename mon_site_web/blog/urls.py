from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentification
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('profil/', views.profil_view, name='profil'),
    
    # Articles
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/<int:article_id>/', views.detail_article, name='detail_article'),
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
]