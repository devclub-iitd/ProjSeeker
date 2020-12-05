from django.conf.urls import include, url
from .views import *
from django.views.generic.base import TemplateView
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required

router = DefaultRouter()
router.register(r'projects',ProjectViewSet)
router.register(r'applications',ApplicationViewSet)
router.register(r'students',StudentViewSet)
router.register(r'profs',ProfViewSet)
router.register(r'interests',InterestViewSet)
router.register(r'bookmarks',BookmarkViewSet)

urlpatterns = [
    url(r"^$", index, name="index"),
    url("",include(router.urls)),
    url(r"^student-profile$",login_required(StudentViewSet.as_view({'get': 'profile'})), name="student-profile"),
    url(r"^delete-student-doc$",login_required(StudentViewSet.as_view({'post': 'delete_file'})), name="delete-student-doc"),
    url(r'^$',TemplateView.as_view(template_name='home.html'),name='home'),
    url(r'^dashboard$',TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),
    
    url(r'^applied-projects$', login_required(ProjectViewSet.as_view({'get': 'get_applied'}), login_url='/accounts/login'), name='applied-projects'),
    url(r'^bookmarked-projects$', login_required(ProjectViewSet.as_view({'get': 'get_bookmarked'}), login_url='/accounts/login'), name='bookmarked-projects'),
    url(r'^find-interests$', login_required(InterestViewSet.as_view({'get': 'find_interests'}), login_url='/accounts/login'), name='find-interests'),
]
