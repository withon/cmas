from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.decorators.http import require_http_methods
from django.urls import reverse

# Create your views here.


def login(request):
    if request.method == 'POST':
        from_page = request.POST.get('from')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            from_page = request.POST.get('from', '/')
            referer = redirect('%s' % from_page)
            return referer
        else:
            return render(request, 'login.html', {'error_message': '用户名或密码不正确', 'from': from_page})
    else:
        context = {}
        context['from'] = request.GET.get('from', reverse('index'))
        print('这里是GET——from：', context['from'])
        return render(request, 'login.html', context)


@require_http_methods(['GET'])
def logout(request):
    auth.logout(request)
    referer = request.META.get('HTTP_REFERER', reverse('index'))
    return redirect(referer)


def change_passwd(request):
    if not request.user.is_authenticated:
        return redirect(reverse('index'))
    user = request.user       # 获取用户名

    if request.method == 'POST':

        old_password = request.POST.get(
            "old_password", "")    # 获取原来的密码，默认为空字符串
        new_password = request.POST.get("new_password", "")    # 获取新密码，默认为空字符串
        confirm = request.POST.get("confirm_password", "")     # 获取确认密码，默认为空字符串
        
        if user.check_password(old_password):               # 到数据库中验证旧密码通过
            if not new_password and confirm:                     # 新密码或确认密码为空
                msg = "新密码不能为空"
                return render(request, "change_passwd.html", {"error_message": msg})
            elif new_password != confirm:                   # 新密码与确认密码不一样
                msg = "两次密码不一致"
                return render(request, "change_passwd.html", {"error_message": msg})

            else:
                try:
                    user.set_password(new_password)             # 修改密码
                    user.save()
                    msg = '修改密码成功'
                    return render(request, "message.html", {"success_message": msg})
                except:
                    msg = '修改密码失败'
                    return render(request, "message.html", {"error_message": msg})
        else:
            msg = "旧密码输入错误"
            return render(request, "change_passwd.html", {"error_message": msg})

    else:
        return render(request, 'change_passwd.html')
