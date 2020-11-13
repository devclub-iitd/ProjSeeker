from django.conf.urls import url
from .views import index, dashboard
from django.views.generic.base import TemplateView
from django.urls import path

urlpatterns = [
    url(r"^index$", index, name="index"),
    url('',TemplateView.as_view(template_name='dashboard.html'),name='home'),
]
