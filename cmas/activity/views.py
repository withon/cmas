from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from datetime import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Activity, Registration, Mnotice, Sysnotice

# Create your views here.
User = get_user_model()


def page_not_found(request):

    return render(request, 'project_error/404.html')


def page_error(request):

    return render(request, 'project_error/500.html')


def permission_denied(request):

    return render(request, 'project_error/403.html')


def index(request):
    context = {}
    all_activities = Activity.objects.all()
    if all_activities:
        latest_activity = all_activities.order_by('-rtime').first()
        context['latest_activity'] = latest_activity

    return render(request, 'index.html', context)


def act_dtl(request, activity_id):
    context = {}
    context['is_select'] = False
    if request.user.is_authenticated:
        if Registration.objects.filter(user_id=request.user.pk, act_id=activity_id):
            context['is_select'] = True
    activity = get_object_or_404(Activity, pk=activity_id)
    activity.cnt = Registration.objects.filter(act_id=activity.id).count()
    context['activity'] = activity
    context['now'] = now()

    return render(request, 'act_dtl.html', context)


def act_list(request):
    context = {}

    context['now'] = now()
    act_types = Activity.objects.values('act_type').distinct().order_by()
    context['act_types'] = act_types
    all_activities = Activity.objects.all().order_by('-rtime')

    if request.user.is_authenticated:
        context['selects'] = all_activities.filter(
            registration__user_id=User.objects.filter(pk=request.user.pk).first())

    if request.GET.get('is_search'):
        start_time = request.GET.get('start_time')
        if start_time:
            all_activities = all_activities.filter(ftime__gt=start_time)
            context['form_start_time'] = start_time

        finish_time = request.GET.get('finish_time')
        if finish_time:
            all_activities = all_activities.filter(stime__lt=finish_time)
            context['form_finish_time'] = finish_time

        act_type = request.GET.get('act_type')
        if act_type == '全部':
            act_type = ''
        if act_type:
            all_activities = all_activities.filter(act_type=act_type)
            context['form_act_type'] = act_type

        apply_only = request.GET.get('apply_only')
        if apply_only and request.user.is_authenticated:
            user = User.objects.filter(pk=request.user.pk).first()
            all_activities = all_activities.filter(registration__user_id=user)
            context['form_apply_only'] = True

    for activity in all_activities:
        cnt = Registration.objects.filter(act_id=activity.id).count()
        activity.cnt = cnt
    context['activities'] = all_activities

    return render(request, 'list.html', context)


@require_http_methods(['POST'])
def select(request):
    if not request.user.is_authenticated:
        return redirect(reverse('index'))

    activity = Activity.objects.get_object_or_404(
        pk=request.POST.get('activity'))
    activity.cnt = Registration.objects.filter(act_id=activity.id).count()
    if activity.stime > now() or activity.ftime < now():
        return redirect(reverse('index'))

    if activity.max_num <= activity.cnt:
        return render(request, 'message.html', {'error_message': '报名失败，名额已满。'})

    user = User.objects.get_object_or_404(pk=request.user.pk)
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
            return render(request, 'message.html', context)

        content = request.POST.get('act_content', '').strip()
        if content == '':
            context['error_message'] = '请填写详情'
            return render(request, 'message.html', context)

        act_type = request.POST.get('act_type', '').strip()
        if act_type == '':
            context['error_message'] = '请填写活动类型'
            return render(request, 'message.html', context)

        start_time = request.POST.get('start_time', '').strip()
        if start_time == '':
            context['error_message'] = '请填写开始时间'
            return render(request, 'message.html', context)

        finish_time = request.POST.get('finish_time', '').strip()
        if finish_time == '':
            context['error_message'] = '请填写结束时间'
            return render(request, 'message.html', context)

        if start_time >= finish_time:
            context['error_message'] = '开始时间需在结束时间之前'
            return render(request, 'message.html', context)
        try:
            max_num = int(request.POST.get('max_num', '').strip())
        except:
            context['error_message'] = '人数上限不合法'
            return render(request, 'message.html', context)

        user = User.objects.filter(pk=request.user.pk).first()

        activity = Activity(title=title, content=content, stime=start_time, ftime=finish_time,
                            act_type=act_type, max_num=max_num, user_id=user)

        try:
            activity.save()
        except:
            context['error_message'] = '出现未知错误，创建失败，请联系系统管理员。'
            return render(request, 'message.html', context)

        act_id = Activity.objects.all().order_by('-rtime').first().pk
        sys_content = '<strong>%s</strong> <span>创建</span> <strong>%s</strong> 类型活动 <strong>%s</strong>(id:%s)<br>开始时间为：%s 结束时间为：%s<br>人数上限为：%s' % (
            user.name, act_type, title, act_id, start_time, finish_time, max_num)
        sysnotice = Sysnotice(content=sys_content, user_id=user)
        sysnotice.save()

        return redirect(reverse('act_list'))

    else:
        return render(request, 'create_act.html', context)


def edit_act(request):
    if not request.user.is_authenticated:
        redirect(reverse('index'))

    if not request.user.is_staff:
        redirect(reverse('index'))

    context = {}

    if request.method == 'GET':
        activity_id = request.GET.get('from')
        print('ACTIVITYID', activity_id)
        activity = Activity.objects.get(pk=activity_id)
        print(activity)
        if not activity:
            redirect(reverse('index'))

        context['activity'] = activity
        return render(request, 'edit_act.html', context)

    else:
        activity = Activity.objects.get(pk=request.POST.get('act_id', ''))
        print(activity.pk)

        title = request.POST.get('act_title', '').strip()
        if title == '':
            context['error_message'] = '请填写标题'
            return render(request, 'message.html', context)

        content = request.POST.get('act_content', '').strip()
        if content == '':
            context['error_message'] = '请填写详情'
            return render(request, 'message.html', context)

        act_type = request.POST.get('act_type', '').strip()
        if act_type == '':
            context['error_message'] = '请填写活动类型'
            return render(request, 'message.html', context)

        start_time = request.POST.get('start_time', '').strip()
        if start_time == '':
            context['error_message'] = '请填写开始时间'
            return render(request, 'message.html', context)

        finish_time = request.POST.get('finish_time', '').strip()
        if finish_time == '':
            context['error_message'] = '请填写结束时间'
            return render(request, 'message.html', context)

        if not start_time < finish_time:
            context['error_message'] = '请检查日期格式xxxx-xx-xx xx:xx'
            return render(request, 'message.html', context)
        try:
            max_num = int(request.POST.get('max_num', '').strip())
        except:
            context['error_message'] = '人数上限不合法'
            return render(request, 'message.html', context)

        user = User.objects.filter(pk=request.user.pk).first()

        activity.title = title
        activity.content = content
        activity.act_type = act_type
        activity.stime = start_time
        activity.ftime = finish_time
        activity.max_num = max_num

        try:
            activity.save()
        except:
            context['error_message'] = '出现未知错误，创建失败，请检查表单格式，或联系系统管理员。'
            return render(request, 'message.html', context)

        act_id = Activity.objects.all().order_by('-rtime').first().pk
        sys_content = '<strong>%s</strong> <span>修改</span> <strong>%s</strong> 类型活动 <strong>%s</strong>(id:%s)<br>开始时间为：%s 结束时间为：%s<br>人数上限为：%s' % (
            user.name, act_type, title, act_id, start_time, finish_time, max_num)
        sysnotice = Sysnotice(content=sys_content, user_id=user)
        sysnotice.save()

        return redirect(reverse('act_list'))


def sysnotice(request):
    context = {}
    all_sysnotices = Sysnotice.objects.all().order_by('-time')
    context['sysnotices'] = all_sysnotices

    return render(request, 'sysnotice.html', context)
