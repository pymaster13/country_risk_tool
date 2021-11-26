from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import UserLoginForm

def index(request):
    """
    Rendering start page
    """
    
    return render(request, 'index.html', {})

def user_login(request):
    """
    Login user with form's validation
    """

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        
        if login_form.is_valid():
            username = login_form.cleaned_data["email"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username = username , password = password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        login_form = UserLoginForm()
        return render(request, 'login.html', {'login_form': login_form})


def user_logout(request):
    """
    Logout user
    """

    logout(request)
    return redirect('index')
