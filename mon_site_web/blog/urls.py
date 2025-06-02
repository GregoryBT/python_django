from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    
    # Articles
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/<int:article_id>/', views.detail_article, name='detail_article'),
    path('articles/', views.articles, name='articles'),
    path('mes-articles/', views.mes_articles, name='mes_articles'),
    
    # Modération
    path('moderation/', views.moderation, name='moderation'),
    
    # Pages statiques
    path('categories/', views.categories, name='categories'),
    path('auteurs/', views.auteurs, name='auteurs'),
    path('a-propos/', views.a_propos, name='a_propos'),
]