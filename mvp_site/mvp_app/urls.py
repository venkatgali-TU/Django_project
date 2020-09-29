from django.urls import path

from .views import single_user, multi_user, hello_mvp

urlpatterns = [
    # path('', TemplateView.as_view(template_name="mvp/auth.html")),
    path('', hello_mvp, name='hello_mvp'),
    path('single/<int:mvp_id>/<str:req>', single_user, name='single_user'),
    path('multi/<int:mvp_id>/<str:req>', multi_user, name='multi_user')
]
