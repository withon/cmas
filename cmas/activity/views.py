from django.shortcuts import render
from django.http import HttpResponse
from . import models

# Create your views here.
def index(request):
    content = {}
    

    return render(request, 'index.html', content)
