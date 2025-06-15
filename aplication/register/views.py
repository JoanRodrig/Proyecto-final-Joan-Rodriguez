from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model  
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms.usuario import UserForm

User = get_user_model()


# Create your views here.
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()      # crea el usuario con first_name, last_name, email, password, etc.
    # lo loguea
                return redirect('signin')
            except IntegrityError:
                form.add_error(None, "Ya existe un usuario con esos datos.")
    else:
        form = UserForm()

    return render(request, "register/signup.html", {
        "form": form,
    })

def signout(request):
    logout(request)
    return redirect('index')

def signin(request):
    if request.method == "GET":
        return render(request, 'register/signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'register/signin.html', {
            'form': AuthenticationForm,
            'error': 'Usuario o Contraseña incorrecta'
        })
        else:
            login(request, user)
            return redirect('index')
            
