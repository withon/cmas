from django.urls import path
from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('activity/', views.act_list, name='act_list'),
    path('activity/<int:activity_id>/', views.act_dtl, name='act_dtl'),
]