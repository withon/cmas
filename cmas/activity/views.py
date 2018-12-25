from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import User, Activity, Registration, Mnotice, Sysnotice

# Create your views here.


def index(request):
    context = {}
    all_activities = Activity.objects.all()
    latest_activity = all_activities.order_by('-rtime')[0]
    context['latest_activity'] = latest_activity

    return render(request, 'index.html', context)

def act_dtl(request, activity_id):
    context = {}
    activity = get_object_or_404(Activity, pk=activity_id)
    context['activity'] = activity

    return render(request, 'act_dtl.html', context)
