from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.decorators.http import require_http_methods
from django.urls import reverse

# Create your views here.


def login(request):
    referer = redirect(request.GET.get('from'), reverse('index'))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return referer
        else:
            return render(request, 'login.html', {'error_message': '用户名或密码不正确'})
    else:
        return render(request, 'login.html', {})

@require_http_methods(['GET'])
def logout(request):
    auth.logout(request)
    return render(request, 'login.html', {})
