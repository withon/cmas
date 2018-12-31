from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Activity, Registration, Sysnotice
import xlwt
from io import BytesIO

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

    paginator = Paginator(all_activities, 10)
    page_num = request.GET.get('page', 1)
    page_of_activities = paginator.get_page(page_num)
    current_page_num = page_of_activities.number
    page_range = list(range(max(current_page_num-2, 1), current_page_num)) + \
        list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    if page_range[0] - 1 > 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    

    context['activities'] = page_of_activities.object_list
    context['page_of_activities'] = page_of_activities
    context['page_range'] = page_range

    return render(request, 'list.html', context)


@require_http_methods(['POST'])
def select(request):
    if not request.user.is_authenticated:
        return redirect(reverse('index'))

    activity = get_object_or_404(Activity, pk=request.POST.get('activity'))
    activity.cnt = Registration.objects.filter(act_id=activity.id).count()
    if activity.stime > now() or activity.ftime < now():
        return redirect(reverse('index'))

    if activity.max_num <= activity.cnt:
        return render(request, 'message.html', {'error_message': '报名失败，名额已满。'})

    user = get_object_or_404(User, pk=request.user.pk)
    registration = Registration(user_id=user, act_id=activity)

    registration.save()

    referer = request.META.get('HTTP_REFERER', reverse('index'))
    return redirect(referer)


def create_act(request):
    context = {}
    act_types = Activity.objects.values('act_type').distinct().order_by()
    context['act_types'] = act_types

    if not request.user.is_authenticated:
        return redirect(reverse('index'))

    if not request.user.is_staff:
        return redirect(reverse('index'))

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
        return redirect(reverse('index'))

    if not request.user.is_staff:
        return redirect(reverse('index'))

    user = User.objects.get(pk=request.user.pk)

    context = {}

    if request.method == 'GET':
        activity_id = request.GET.get('from')
        activity = Activity.objects.get(pk=activity_id)
        if not activity:
            redirect(reverse('index'))

        context['activity'] = activity
        return render(request, 'edit_act.html', context)

    else:
        activity = Activity.objects.get(pk=request.POST.get('act_id', ''))

        if not activity.is_freeze:

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


            activity.title = title
            activity.content = content
            activity.act_type = act_type
            activity.stime = start_time
            activity.ftime = finish_time
            activity.max_num = max_num

        try:
            point = float(request.POST.get('point', '').strip())
            activity.point = point
        except:
            context['error_message'] = '分值设置错误'
            return render(request, 'message.html', context)
        
        is_freeze = request.POST.get('freeze')
        if is_freeze:
            activity.is_freeze = True

        try:
            activity.save()
        except:
            context['error_message'] = '出现未知错误，创建失败，请检查表单格式，或联系系统管理员。'
            return render(request, 'message.html', context)

        act_id = Activity.objects.all().order_by('-rtime').first().pk
        sys_content = '<strong>%s</strong> <span>修改</span> <strong>%s</strong> 类型活动 <strong>%s</strong>(id:%s)<br>开始时间为：%s 结束时间为：%s<br>人数上限为：%s 分值为：%s<br>冻结状态为：%s' % (
            user.name, activity.act_type, activity.title, activity.pk, activity.stime, activity.ftime, activity.max_num, activity.point, activity.is_freeze)
        sysnotice = Sysnotice(content=sys_content, user_id=user)
        sysnotice.save()

        return redirect(reverse('act_list'))


def sysnotice(request):
    context = {}
    all_sysnotices = Sysnotice.objects.all().order_by('-time')
    context['sysnotices'] = all_sysnotices

    return render(request, 'sysnotice.html', context)


def export(request):
    if not request.user.is_authenticated:
        return redirect(reverse('index'))

    if not request.user.is_staff:
        return redirect(reverse('index'))

    if request.method == 'GET':
        return render(request, 'export.html')
    else:
        export_type = request.POST.get('export_act')
        start_time = request.POST.get('start_time')
        finish_time = request.POST.get('finish_time')

        if export_type == 'act':
            activities = Activity.objects.all()
            if start_time:
                activities = activities.filter(ftime__gte=start_time)
            if finish_time:
                activities = activities.filter(stime__lte=finish_time)
            return export_act(activities)
        elif export_type == 'reg':
            registrations = Registration.objects.all()
            if start_time:
                registrations = registrations.filter(act_id__ftime__gte=start_time)
            if finish_time:
                registrations = registrations.filter(act_id__stime__lte=finish_time)
                
            return export_reg(registrations)
        else:
            pass


def export_act(request):
    activities = Activity.objects.all()
    # 设置HTTPResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=activity.xls'
    # 创建一个文件对象
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('registion-sheet')
    # 设置文件头的样式,这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

    # 写入文件标题
    sheet.write(0, 0, '活动id', style_heading)
    sheet.write(0, 1, '活动名称', style_heading)
    sheet.write(0, 2, '报名起始时间', style_heading)
    sheet.write(0, 3, '报名结束时间', style_heading)
    sheet.write(0, 4, '活动类型', style_heading)
    sheet.write(0, 5, '分值', style_heading)
    sheet.write(0, 6, '报名人数', style_heading)
    sheet.write(0, 7, '名额', style_heading)
    sheet.write(0, 8, '发起者', style_heading)

    registrations = Registration.objects.all()

    # 写入数据
    data_row = 1

    for i in activities:
            # 格式化datetime
        sheet.write(data_row, 0, i.pk)
        sheet.write(data_row, 1, i.title)
        stime = i.stime.strftime('%Y-%m-%d')
        ftime = i.ftime.strftime('%Y-%m-%d')
        sheet.write(data_row, 2, stime)
        sheet.write(data_row, 3, ftime)
        sheet.write(data_row, 4, i.act_type)
        sheet.write(data_row, 5, i.point)
        sheet.write(data_row, 6, registrations.filter(act_id=i).count())
        sheet.write(data_row, 7, i.max_num)
        sheet.write(data_row, 8, i.user_id.name)

        data_row = data_row + 1


    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


def export_reg(request):
    registrations = Registration.objects.all()
    # 设置HTTPResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=registion.xls'
    # 创建一个文件对象
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('registion-sheet')
    # 设置文件头的样式,这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

    # 写入文件标题
    sheet.write(0, 0, 'id', style_heading)
    sheet.write(0, 1, '活动名称', style_heading)
    sheet.write(0, 2, '活动id', style_heading)
    sheet.write(0, 3, '分值', style_heading)
    sheet.write(0, 4, '姓名', style_heading)
    sheet.write(0, 5, '学号', style_heading)
    sheet.write(0, 6, '报名日期', style_heading)

    # 写入数据
    data_row = 1

    for i in registrations:
            # 格式化datetime
        sheet.write(data_row, 0, i.pk)
        sheet.write(data_row, 1, i.act_id.title)
        sheet.write(data_row, 2, i.act_id.pk)
        sheet.write(data_row, 3, i.act_id.point)
        sheet.write(data_row, 4, i.user_id.name)
        sheet.write(data_row, 5, i.user_id.username)
        reg_time = i.time.strftime('%Y-%m-%d')
        sheet.write(data_row, 6, reg_time)

        data_row = data_row + 1


    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

