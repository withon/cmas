from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.urls import reverse
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
    context['is_select'] = False
    if request.user.is_authenticated:
        if Registration.objects.filter(user_id=request.user.pk, act_id=activity_id):
            context['is_select'] = True
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
        all_activities = Activity.objects.filter(
            ftime__gte=start_time, stime__lte=end_time).order_by('-stime')
        if act_type:
            all_activities = all_activities.filter(act_type=act_type)

    else:
        all_activities = Activity.objects.all().order_by('-rtime')
    for activity in all_activities:
        cnt = Registration.objects.filter(act_id=activity.id).count()
        activity.cnt = cnt
    context['activities'] = all_activities

    return render(request, 'list.html', context)


@require_http_methods(['POST'])
def select(request):
    if not request.user.is_authenticated:
        return redirect(reverse('index'))
    activity = Activity.objects.filter(pk=request.POST.get('activity')).first()
    user = User.objects.filter(pk=request.user.pk).first()
    registration = Registration(user_id=user, act_id=activity)
    registration.save()
    referer = request.META.get('HTTP_REFERER', reverse('index'))

    return redirect(referer)


def create_act(request):
    context = {}
    act_types = Activity.objects.values('act_type').distinct().order_by()
    context['act_types'] = act_types

    if not request.user.is_authenticated:
        redirect(reverse('index'))

    if not request.user.is_staff:
        redirect(reverse('index'))

    if request.method == 'POST':

        title = request.POST.get('act_title', '').strip()
        if title == '':
            context['error_message'] = '请填写标题'
            return render(request, 'create_act.html', context)

        content = request.POST.get('act_content', '').strip()
        if content == '':
            context['error_message'] = '请填写详情'
            return render(request, 'create_act.html', context)

        act_type = request.POST.get('act_type', '').strip()
        if act_type == '':
            context['error_message'] = '请填写活动类型'
            return render(request, 'create_act.html', context)

        start_time = request.POST.get('start_time', '').strip()
        if start_time == '':
            context['error_message'] = '请填写开始时间'
            return render(request, 'create_act.html', context)

        finish_time = request.POST.get('finish_time', '').strip()
        if finish_time == '':
            context['error_message'] = '请填写结束时间'
            return render(request, 'create_act.html', context)

        if start_time >= finish_time:
            context['error_message'] = '开始时间需在结束时间之前'
            return render(request, 'create_act.html', context)
        try:
            max_num = int(request.POST.get('max_num', '').strip())
        except:
            context['error_message'] = '人数上限不合法'
            return render(request, 'create_act.html', context)

        user = User.objects.filter(pk=request.user.pk).first()

        activity = Activity(title=title, content=content, stime=start_time, ftime=finish_time,
                            act_type=act_type, max_num=max_num, user_id=user)

        try:
            activity.save()
        except:
            context['error_message'] = '出现未知错误，创建失败，请联系系统管理员。'
            return render(request, 'create_act.html', context)

        act_id = Activity.objects.all().order_by('-rtime').first().pk
        sys_content = '<strong>%s</strong> <span>创建</span> <strong>%s</strong> 类型活动 <strong>%s</strong>(id:%s)<br>开始时间为：%s 结束时间为：%s<br>人数上限为：%s' % (
            user.name, act_type, title, act_id, start_time, finish_time, max_num)
        sysnotice = Sysnotice(content=sys_content, user_id=user)
        sysnotice.save()


        return redirect(reverse('act_list'))

    else:
        return render(request, 'create_act.html', context)


def sysnotice(request):
    context = {}
    all_sysnotices = Sysnotice.objects.all().order_by('-time')
    context['sysnotices'] = all_sysnotices

    return render(request, 'sysnotice.html', context)
