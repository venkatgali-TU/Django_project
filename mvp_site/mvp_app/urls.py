from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from django.urls import path, include
from .views import hello_mvp, single_user, multi_user, MvpViewSet, data_view, request_detail, request_list, \
    profile_upload

router = routers.DefaultRouter()
router.register(r'irabot', MvpViewSet)

urlpatterns = [
    path('', hello_mvp, name='hello_mvp'),
    path('data/', data_view, name='data_view'),
    path('single/<int:mvp_id>/<str:req>', single_user, name='single_user'),
    path('multi/<int:mvp_id>/<str:req>', multi_user, name='multi_user'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^get-requests/$', request_list),
    url(r'^update-requests/(?P<pk>[0-9]+)$', request_detail),
    # path('', include(router.urls)),
    path('upload-csv/', profile_upload, name="profile_upload"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
