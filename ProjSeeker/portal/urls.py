from django.conf.urls import url
from .views import index
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r"^index$", index, name="index"),
    url('',TemplateView.as_view(template_name='home.html'),name='home'),
    
]
