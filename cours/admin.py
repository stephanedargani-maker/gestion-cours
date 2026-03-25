from django.contrib import admin
from .models import Cours, Inscription, ProfilUtilisateur


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display   = ['titre', 'enseignant', 'createur', 'date_publication']
    list_filter    = ['date_publication', 'enseignant']
    search_fields  = ['titre', 'enseignant']
    ordering       = ['-date_publication']
    date_hierarchy = 'date_publication'


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display  = ['etudiant', 'cours', 'date_inscription']
    list_filter   = ['cours']
    search_fields = ['etudiant__username', 'cours__titre']


@admin.register(ProfilUtilisateur)
class ProfilAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role']
    list_filter   = ['role']


admin.site.site_header  = 'GestionCours — Administration'
admin.site.site_title   = 'GestionCours'
admin.site.index_title  = "Tableau de bord"
