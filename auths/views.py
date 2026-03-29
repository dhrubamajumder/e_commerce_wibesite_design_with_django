from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from . forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages

# Create your views here.



def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1']
        )
        return redirect('login')
    return render(request, 'auths/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('product_list')

        else:
            error = "Invalid username or password"
            return render(request, 'auths/login.html', {'error': error})

    return render(request, 'auths/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
