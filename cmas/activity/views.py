from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .models import Activity, Registration, Mnotice, Sysnotice

# Create your views here.
User = get_user_model()


def index(request):
    context = {}
    all_activities = Activity.objects.all()
    if all_activities:
        latest_activity = all_activities.order_by('-rtime')[0]
        context['latest_activity'] = latest_activity

    return render(request, 'index.html', context)

def act_dtl(request, activity_id):
    context = {}
    activity = get_object_or_404(Activity, pk=activity_id)
    context['activity'] = activity

    return render(request, 'act_dtl.html', context)

def act_list(request):
    context = {}
    act_types = Activity.objects.values('act_type').distinct().order_by()
    context['act_types'] = act_types
    if request.GET.get('is_select'):
        start_time = request.GET.get('start_time', '')
        end_time = request.GET.get('end_time', '')
        act_type = request.GET.get('act_type', '')
        if act_type == '全部':
            act_type = ''
        apply_only = request.GET.get('apply_only', '')
        all_activities = Activity.objects.filter(ftime__gte=start_time, stime__lte=end_time).order_by('-stime')
        if act_type:
            all_activities = all_activities.filter(act_type=act_type)
        
    else:
        all_activities = Activity.objects.all().order_by('-rtime')
    for activity in all_activities:
        cnt = Registration.objects.filter(act_id=activity.id).count()
        activity.cnt = cnt
    context['activities'] = all_activities

    return render(request, 'list.html', context)

