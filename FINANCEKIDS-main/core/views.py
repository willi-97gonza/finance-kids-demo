from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from core.forms import RegistroForm
from game.models import UserProfile


def _get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(usuario=user)
    return profile


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'core/login.html')


@login_required
def index(request):
    profile = _get_user_profile(request.user)
    return render(request, 'core/index.html', {'progreso_actual': profile.ultimo_tema_desbloqueado})


@require_http_methods(['GET', 'POST'])
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect('login')
        return render(request, 'core/registro.html', {'form': form})

    return render(request, 'core/registro.html', {'form': RegistroForm()})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def aprendizaje(request, tema):
    tema_actual = _get_user_profile(request.user).ultimo_tema_desbloqueado

    if tema > tema_actual:
        return render(request, "core/bloqueado.html", {"tema": tema})
    return render(request, f"core/aprendizaje{tema}.html")


@login_required
@require_POST
def completar_tema(request, tema):
    profile = _get_user_profile(request.user)
    tema_actual = profile.ultimo_tema_desbloqueado

    if tema >= tema_actual:
        profile.ultimo_tema_desbloqueado = tema + 1
        profile.save(update_fields=['ultimo_tema_desbloqueado'])

    siguiente_tema = tema + 1
    MAX_TEMAS = 10
    if siguiente_tema > MAX_TEMAS:
        return redirect('index')

    return redirect('aprendizaje', tema=siguiente_tema)


@login_required
def juego1(request):
    return render(request, 'core/juego1.html')


@login_required
def preguntas1(request):
    return render(request, 'core/preguntas1.html')


@login_required
def juego2(request):
    return render(request, 'core/juego2.html')


@login_required
def preguntas2(request):
    return render(request, 'core/preguntas2.html')
