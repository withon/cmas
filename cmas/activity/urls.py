from django.urls import path
from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('activity/', views.act_list, name='act_list'),
    path('activity/<int:activity_id>/', views.act_dtl, name='act_dtl'),
    path('activity/select/', views.select, name='select'),
    path('activity/create/', views.create_act, name='create_act'),
    path('sysnotice/', views.sysnotice, name='sysnotice')
]