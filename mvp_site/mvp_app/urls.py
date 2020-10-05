from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from django.urls import path

from django.urls import path, include
from .views import hello_mvp, single_user, multi_user

urlpatterns = [
    path('', hello_mvp, name='hello_mvp'),
    path('single/<int:mvp_id>/<str:req>', single_user, name='single_user'),
    path('multi/<int:mvp_id>/<str:req>', multi_user, name='multi_user'),
    url(r'^accounts/', include('allauth.urls'))
]
