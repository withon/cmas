from django.contrib import admin
from .models import Activity, Registration, Mnotice, Sysnotice

# Register your models here.
#admin.site.register(User)User,
admin.site.register(Activity)
admin.site.register(Registration)
admin.site.register(Mnotice)
admin.site.register(Sysnotice)
