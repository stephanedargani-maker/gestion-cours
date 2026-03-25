from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    # Pages publiques
    path('', views.accueil, name='liste'),
    path('cours/', views.liste_cours, name='liste_cours'),
    path('cours/<int:pk>/', views.detail_cours, name='detail'),

    # CRUD cours (enseignant + admin)
    path('cours/ajouter/', views.ajouter_cours, name='ajouter_cours'),
    path('cours/<int:pk>/modifier/', views.modifier_cours, name='modifier_cours'),
    path('cours/<int:pk>/supprimer/', views.supprimer_cours, name='supprimer_cours'),

    # Inscriptions (étudiant)
    path('cours/<int:pk>/inscrire/', views.inscrire_cours, name='inscrire_cours'),
    path('cours/<int:pk>/desinscrire/', views.desinscrire_cours, name='desinscrire_cours'),
    path('mes-cours/', views.espace_etudiant, name='espace_etudiant'),

    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('inscription/', views.register, name='register'),

    # Tableau de bord
    path('dashboard/', views.tableau_bord, name='tableau_bord'),

    # Impression
    path('imprimer/', views.imprimer_cours, name='imprimer_cours'),
]
