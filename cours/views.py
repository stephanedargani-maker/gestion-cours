from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Cours, Inscription, ProfilUtilisateur
from .forms import CoursForm, InscriptionForm


# ── Helpers ─────────────────────────────────────────────────────────────────

def get_role(user):
    if not user.is_authenticated:
        return 'anonyme'
    if user.is_superuser:
        return 'admin'
    if user.is_staff:
        return 'enseignant'
    return 'etudiant'


# ── ACCUEIL ─────────────────────────────────────────────────────────────────

def accueil(request):
    derniers_cours = Cours.objects.order_by('-date_publication')[:6]
    total_cours    = Cours.objects.count()
    stats = [
        {'valeur': total_cours, 'label': 'Cours publiés', 'icon': 'book'},
        {'valeur': Cours.objects.values('enseignant').distinct().count(), 'label': 'Enseignants', 'icon': 'user'},
        {'valeur': Inscription.objects.count(), 'label': 'Inscriptions', 'icon': 'users'},
        {'valeur': Cours.objects.filter(date_publication__year=timezone.now().year).count(), 'label': 'Cette année', 'icon': 'calendar'},
    ]
    features = [
        {'titre': 'Création facile', 'desc': "Publiez vos cours en quelques clics depuis votre espace enseignant.", 'color': 'blue'},
        {'titre': 'Accès sécurisé', 'desc': 'Chaque rôle dispose de son propre espace sécurisé par mot de passe.', 'color': 'purple'},
        {'titre': 'Gestion complète', 'desc': 'Créez, modifiez, supprimez et imprimez vos listes de cours.', 'color': 'green'},
    ]
    return render(request, 'cours/accueil.html', {
        'derniers_cours': derniers_cours,
        'total_cours': total_cours,
        'stats': stats,
        'features': features,
        'role': get_role(request.user),
        'admin_perms': ['Gérer tous les cours', 'Gérer les utilisateurs', 'Statistiques globales', 'Accès admin complet', 'Imprimer les listes'],
        'enseignant_perms': ['Créer ses cours', 'Modifier ses cours', 'Supprimer ses cours', 'Voir ses inscrits', 'Imprimer sa liste'],
        'etudiant_perms': ["Voir tous les cours", "S'inscrire aux cours", 'Espace personnel', 'Historique des cours', 'Imprimer mes cours'],
})


# ── LISTE COURS ──────────────────────────────────────────────────────────────

def liste_cours(request):
    query            = request.GET.get('q', '').strip()
    enseignant_filtre = request.GET.get('enseignant', '').strip()
    cours_list       = Cours.objects.order_by('-date_publication')

    if query:
        from django.db.models import Q
        cours_list = cours_list.filter(
            Q(titre__icontains=query) | Q(enseignant__icontains=query)
        )
    if enseignant_filtre:
        cours_list = cours_list.filter(enseignant=enseignant_filtre)

    enseignants = Cours.objects.values_list('enseignant', flat=True).distinct().order_by('enseignant')

    # Cours où l'utilisateur est inscrit
    mes_inscriptions = []
    if request.user.is_authenticated:
        mes_inscriptions = Inscription.objects.filter(etudiant=request.user).values_list('cours_id', flat=True)

    return render(request, 'cours/liste_cours.html', {
        'cours_list': cours_list,
        'query': query,
        'enseignant_filtre': enseignant_filtre,
        'enseignants': enseignants,
        'mes_inscriptions': list(mes_inscriptions),
        'role': get_role(request.user),
    })


# ── DETAIL COURS ─────────────────────────────────────────────────────────────

def detail_cours(request, pk):
    cours           = get_object_or_404(Cours, pk=pk)
    cours_similaires = Cours.objects.filter(enseignant=cours.enseignant).exclude(pk=pk)[:4]
    est_inscrit     = False
    if request.user.is_authenticated:
        est_inscrit = Inscription.objects.filter(etudiant=request.user, cours=cours).exists()

    return render(request, 'cours/detail_cours.html', {
        'cours': cours,
        'cours_similaires': cours_similaires,
        'est_inscrit': est_inscrit,
        'role': get_role(request.user),
        'peut_modifier': cours.peut_modifier(request.user) if request.user.is_authenticated else False,
    })


# ── AJOUTER COURS ────────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def ajouter_cours(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Accès réservé aux enseignants et administrateurs.')
        return redirect('cours:liste_cours')

    if request.method == 'POST':
        form = CoursForm(request.POST)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.createur = request.user
            cours.save()
            messages.success(request, f'Cours "{cours.titre}" créé avec succès !')
            return redirect('cours:detail', pk=cours.pk)
    else:
        form = CoursForm()

    return render(request, 'cours/ajouter_cours.html', {'form': form, 'role': get_role(request.user)})


# ── MODIFIER COURS ───────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def modifier_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)

    if not cours.peut_modifier(request.user):
        messages.error(request, 'Vous n\'avez pas la permission de modifier ce cours.')
        return redirect('cours:detail', pk=pk)

    if request.method == 'POST':
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cours "{cours.titre}" modifié avec succès !')
            return redirect('cours:detail', pk=cours.pk)
    else:
        form = CoursForm(instance=cours)

    return render(request, 'cours/modifier_cours.html', {
        'form': form, 'cours': cours, 'role': get_role(request.user)
    })


# ── SUPPRIMER COURS ──────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def supprimer_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)

    if not cours.peut_modifier(request.user):
        messages.error(request, 'Vous n\'avez pas la permission de supprimer ce cours.')
        return redirect('cours:detail', pk=pk)

    if request.method == 'POST':
        titre = cours.titre
        cours.delete()
        messages.success(request, f'Cours "{titre}" supprimé avec succès !')
        return redirect('cours:liste_cours')

    return render(request, 'cours/supprimer_cours.html', {
        'cours': cours, 'role': get_role(request.user)
    })


# ── INSCRIPTION COURS ────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def inscrire_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)

    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Les enseignants et admins ne peuvent pas s\'inscrire aux cours.')
        return redirect('cours:detail', pk=pk)

    inscription, created = Inscription.objects.get_or_create(etudiant=request.user, cours=cours)
    if created:
        messages.success(request, f'Vous êtes inscrit au cours "{cours.titre}" !')
    else:
        messages.info(request, 'Vous êtes déjà inscrit à ce cours.')

    return redirect('cours:detail', pk=pk)


@login_required(login_url='cours:connexion')
def desinscrire_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    Inscription.objects.filter(etudiant=request.user, cours=cours).delete()
    messages.success(request, f'Vous vous êtes désinscrit du cours "{cours.titre}".')
    return redirect('cours:detail', pk=pk)


# ── ESPACE ÉTUDIANT ──────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def espace_etudiant(request):
    inscriptions = Inscription.objects.filter(etudiant=request.user).select_related('cours')
    return render(request, 'cours/espace_etudiant.html', {
        'inscriptions': inscriptions,
        'role': get_role(request.user),
    })


# ── INSCRIPTION COMPTE ───────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('cours:tableau_bord')

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name or user.username} ! Votre compte a été créé.')
            return redirect('cours:tableau_bord')
    else:
        form = InscriptionForm()

    return render(request, 'registration/register.html', {'form': form})


# ── CONNEXION ────────────────────────────────────────────────────────────────

def connexion(request):
    if request.user.is_authenticated:
        return redirect('cours:tableau_bord')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name or user.username} !')
            return redirect(request.GET.get('next', 'cours:tableau_bord'))
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')

    return render(request, 'cours/connexion.html', {'role': 'anonyme'})


# ── DÉCONNEXION ──────────────────────────────────────────────────────────────

def deconnexion(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Vous avez été déconnecté.')
    return redirect('cours:liste')


# ── TABLEAU DE BORD ──────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def tableau_bord(request):
    now  = timezone.now()
    role = get_role(request.user)

    if role == 'admin':
        context = {
            'derniers_cours': Cours.objects.order_by('-date_publication')[:8],
            'total_cours': Cours.objects.count(),
            'total_enseignants': Cours.objects.values('enseignant').distinct().count(),
            'total_inscrits': Inscription.objects.values('etudiant').distinct().count(),
            'cours_ce_mois': Cours.objects.filter(date_publication__month=now.month, date_publication__year=now.year).count(),
            'top_enseignants': Cours.objects.values('enseignant').annotate(total=Count('id')).order_by('-total')[:5],
            'today': now,
        }
    elif role == 'enseignant':
        mes_cours = Cours.objects.filter(createur=request.user).order_by('-date_publication')
        context = {
            'mes_cours': mes_cours,
            'total_mes_cours': mes_cours.count(),
            'total_inscrits': Inscription.objects.filter(cours__createur=request.user).count(),
            'cours_ce_mois': mes_cours.filter(date_publication__month=now.month, date_publication__year=now.year).count(),
            'today': now,
        }
    else:  # etudiant
        inscriptions = Inscription.objects.filter(etudiant=request.user).select_related('cours')
        context = {
            'inscriptions': inscriptions,
            'total_inscrits': inscriptions.count(),
            'today': now,
        }

    context['role'] = role
    return render(request, 'cours/tableau_bord.html', context)


# ── IMPRESSION ───────────────────────────────────────────────────────────────

@login_required(login_url='cours:connexion')
def imprimer_cours(request):
    role = get_role(request.user)
    if role == 'admin':
        cours_list = Cours.objects.order_by('enseignant', 'titre')
        titre_liste = 'Liste complète des cours'
    elif role == 'enseignant':
        cours_list  = Cours.objects.filter(createur=request.user).order_by('titre')
        titre_liste = f'Mes cours — {request.user.get_full_name() or request.user.username}'
    else:
        cours_list  = Cours.objects.filter(inscrits__etudiant=request.user).order_by('titre')
        titre_liste = f'Mes cours inscrits — {request.user.get_full_name() or request.user.username}'

    return render(request, 'cours/imprimer_cours.html', {
        'cours_list': cours_list,
        'titre_liste': titre_liste,
        'user': request.user,
        'date_impression': now if (now := timezone.now()) else timezone.now(),
        'role': role,
    })
