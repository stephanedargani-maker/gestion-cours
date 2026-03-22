from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    path('', views.accueil, name='liste'),
    path('cours/', views.liste_cours, name='liste_cours'),
    path('cours/<int:pk>/', views.detail_cours, name='detail'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.tableau_bord, name='tableau_bord'),
]