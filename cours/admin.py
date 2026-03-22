from django.contrib import admin
from .models import Cours

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'enseignant', 'date_publication']
    search_fields = ['titre', 'enseignant']
    list_filter   = ['date_publication', 'enseignant']
    ordering      = ['-date_publication']

admin.site.site_header = 'GestionCours — Administration'
admin.site.site_title  = 'GestionCours Admin'
admin.site.index_title = "Tableau de bord"