from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/<int:article_id>/', views.detail_article, name='detail_article'),
    path('articles/', views.articles, name='articles'),
    path('categories/', views.categories, name='categories'),
    path('auteurs/', views.auteurs, name='auteurs'),
    path('a-propos/', views.a_propos, name='a_propos'),
]