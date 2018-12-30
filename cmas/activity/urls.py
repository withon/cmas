from django.urls import path
from . import views

handler403 = views.permission_denied
handler404 = views.page_not_found
handler505 = views.page_error

urlpatterns=[
    path('', views.index, name='index'),
    path('activity/', views.act_list, name='act_list'),
    path('activity/<int:activity_id>/', views.act_dtl, name='act_dtl'),
    path('activity/select/', views.select, name='select'),
    path('activity/create/', views.create_act, name='create_act'),
    path('activity/edit/', views.edit_act, name='edit_act'),
    path('sysnotice/', views.sysnotice, name='sysnotice'),
    path('export/', views.export, name="export"),
    path('export/act/', views.export_act, name="export_act"),
    path('export/reg/', views.export_reg, name="export_reg"),
]