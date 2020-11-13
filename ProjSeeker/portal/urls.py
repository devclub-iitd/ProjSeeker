from django.conf.urls import url
from .views import index, dashboard
from django.views.generic.base import TemplateView
from django.urls import path

urlpatterns = [
    url(r"^index$", index, name="index"),
    url(r'^$',TemplateView.as_view(template_name='home.html'),name='home'),
    url(r'^dashboard$',TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),
]
