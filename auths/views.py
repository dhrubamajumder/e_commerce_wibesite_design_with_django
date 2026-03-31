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
        return redirect('user_login')
    return render(request, 'auths/register.html', {'form': form})



def user_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                return render(request, 'auths/login.html', {
                    'error': "Admin cannot login from user panel."
                })

            login(request, user)
            return redirect('product_list')

        else:
            return render(request, 'auths/login.html', {
                'error': "Invalid username or password"
            })

    return render(request, 'auths/login.html')


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_staff:
                return render(request, 'admin/admin_login.html', {
                    'error': "You are not authorized as admin."
                })

            login(request, user)
            return redirect('admin_dashboard')

        else:
            return render(request, 'admin/admin_login.html', {
                'error': "Invalid username or password"
            })

    return render(request, 'admin/admin_login.html')



def logout_view(request):
    logout(request)
    return redirect('user_login')
