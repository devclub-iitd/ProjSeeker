from django.conf.urls import include, url
from .views import *
from django.views.generic.base import TemplateView
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'students', StudentViewSet)
router.register(r'profs', ProfViewSet)
router.register(r'interests', InterestViewSet)
router.register(r'bookmarks', BookmarkViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r"^index$", index, name="index"),
    url(r"^auth/iitd/confirm$", authenticate, name="auth-iitd"),
    url("", include(router.urls)),
    url(r"^student-profile$",
        login_required(StudentViewSet.as_view({'get': 'profile'})), name="student-profile"),
    url(r"^check-documents$",
        login_required(StudentViewSet.as_view({'post': 'check_documents'})), name="document-check"),
    url(r"^delete-student-doc$", login_required(StudentViewSet.as_view(
        {'post': 'delete_file'})), name="delete-student-doc"),
    url(r"^prof-profile$",
        login_required(ProfViewSet.as_view({'get': 'profile'})), name="prof-profile"),
    url(r"^delete-prof-doc$",
        login_required(ProfViewSet.as_view({'post': 'delete_file'})), name="delete-prof-doc"),
    url(r'^dashboard$', dashboard, name='dashboard'),
    url(r'^find-projects',
        ProjectViewSet.as_view({'get': 'find_projects'}), name="find-projects"),
    url(r'^my-projects$',
        ProjectViewSet.as_view({'get': 'my_projects'}),  name='my-projects'),
    url(r'^applied-projects$',
        ProjectViewSet.as_view({'get': 'applied_projects'}),  name='applied-projects'),
    url(r'^new-project$',
        ProjectViewSet.as_view({'get': 'create_new_project'}), name='new-project'),
    url(r'^received-applications$', ApplicationViewSet.as_view(
        {'get': 'list_received_applications'}), name='list-received-applications'),
    url(r'^view-applications$', ApplicationViewSet.as_view(
        {'get': 'view_received_applications'}), name='view-received-applications'),
    url(r'^auth/iitd$', iitd_redirect, name='iitd_redirect'),
    path('uploads/user_<int:pk>/<str:file_name>',
         get_uploaded_file, name='get-uploaded-file'),
]
