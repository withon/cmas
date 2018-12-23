from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Activity, Registration, Mnotice, Sysnotice

# Create your views here.
def index(request):
    content = {}
    all_activities = Activity.objects.all()
    latest_activity = all_activities.order_by('-rtime')[0]
    content['latest_activity'] = latest_activity

    return render(request, 'index.html', content)
