from django.conf.urls import include, url
from .views import *
from django.views.generic.base import TemplateView
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'projects',ProjectViewSet)
router.register(r'applications',ApplicationViewSet)
router.register(r'students',StudentViewSet)
router.register(r'profs',ProfViewSet)
router.register(r'interests',InterestViewSet)

urlpatterns = [
    url("",include(router.urls)),
    url(r"^index$", index, name="index"),
    url(r'^$',TemplateView.as_view(template_name='home.html'),name='home'),
    url(r'^dashboard$',TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),
]
