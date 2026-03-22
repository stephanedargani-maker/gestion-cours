from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from .models import Cours

def accueil(request):
    derniers_cours = Cours.objects.order_by('-date_publication')[:6]
    total_cours = Cours.objects.count()
    stats = [
        {'valeur': total_cours, 'label': 'Cours publiés'},
        {'valeur': Cours.objects.values('enseignant').distinct().count(), 'label': 'Enseignants'},
        {'valeur': Cours.objects.filter(date_publication__month=timezone.now().month).count(), 'label': 'Cours ce mois'},
        {'valeur': Cours.objects.filter(date_publication__year=timezone.now().year).count(), 'label': "Cette année"},
    ]
    features = [
        {'icon': '<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>', 'titre': 'Création facile', 'desc': "Ajoutez des cours en quelques secondes via l'interface d'administration Django."},
        {'icon': '<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>', 'titre': 'Accès sécurisé', 'desc': 'Authentification par mot de passe pour les administrateurs.'},
        {'icon': '<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>', 'titre': 'Recherche rapide', 'desc': 'Trouvez un cours par titre ou enseignant instantanément.'},
    ]
    return render(request, 'cours/accueil.html', {
        'derniers_cours': derniers_cours,
        'total_cours': total_cours,
        'stats': stats,
        'features': features,
    })

def liste_cours(request):
    query = request.GET.get('q', '').strip()
    enseignant_filtre = request.GET.get('enseignant', '').strip()
    cours_list = Cours.objects.order_by('-date_publication')
    if query:
        cours_list = cours_list.filter(titre__icontains=query) | Cours.objects.filter(enseignant__icontains=query)
        cours_list = cours_list.distinct()
    if enseignant_filtre:
        cours_list = cours_list.filter(enseignant=enseignant_filtre)
    enseignants = Cours.objects.values_list('enseignant', flat=True).distinct().order_by('enseignant')
    return render(request, 'cours/liste_cours.html', {
        'cours_list': cours_list,
        'query': query,
        'enseignant_filtre': enseignant_filtre,
        'enseignants': enseignants,
    })

def detail_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    cours_similaires = Cours.objects.filter(enseignant=cours.enseignant).exclude(pk=cours.pk)[:4]
    return render(request, 'cours/detail_cours.html', {
        'cours': cours,
        'cours_similaires': cours_similaires,
    })

def connexion(request):
    if request.user.is_authenticated:
        return redirect('cours:tableau_bord')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('cours:tableau_bord')
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    return render(request, 'cours/connexion.html', {'form': {}})

def deconnexion(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Déconnecté avec succès.')
    return redirect('cours:liste')

@login_required(login_url='cours:connexion')
def tableau_bord(request):
    now = timezone.now()
    return render(request, 'cours/tableau_bord.html', {
        'derniers_cours': Cours.objects.order_by('-date_publication')[:8],
        'total_cours': Cours.objects.count(),
        'total_enseignants': Cours.objects.values('enseignant').distinct().count(),
        'cours_ce_mois': Cours.objects.filter(date_publication__month=now.month, date_publication__year=now.year).count(),
        'top_enseignants': Cours.objects.values('enseignant').annotate(total=Count('id')).order_by('-total')[:5],
        'today': now,
    })