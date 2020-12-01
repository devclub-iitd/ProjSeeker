from django.shortcuts import render
from django.http.response import HttpResponse
from django.urls.base import reverse_lazy
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import *
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework import permissions

# Create your views here.
def index(request):
    return render(request, 'home.html');


def dashboard(request):
    return render(request, 'dashboard.html')

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        bookmark = { 'is_bmkd': False, 'bmk': None } 
        if (request.user.is_authenticated):
            bmk = Bookmark.objects.filter(user=request.user).filter(project=instance)
            bookmark['is_bmkd'] = len(bmk) != 0
            bookmark['bmk'] = bmk[0] if (bookmark['is_bmkd']) else None
        return render(request,template_name='project-detail.html', context={'project': serializer.data, 'bookmark' : bookmark})

    def list(self, request, *args, **kwargs):
        qset = self.get_queryset()
        serializer = self.get_serializer(qset, many=True)
        return render(request, template_name="dashboard.html", context={'projects': serializer.data})

    @action(detail=False)
    def get_applied(self, request):
        user = request.user
        applied = Application.objects.filter(student__user=user)
        projects = [appl.project for appl in applied]
        serializer = self.get_serializer(projects, many=True)
        return render(request, template_name="dashboard.html", context={'projects': serializer.data})
    
    @action(detail=False)
    def get_bookmarked(self, request):
        user = request.user
        bookmarked = Bookmark.objects.filter(user=user)
        projects = [bmk.project for bmk in bookmarked]
        serializer = self.get_serializer(projects, many=True)
        return render(request, template_name="dashboard.html", context={'projects': serializer.data})

class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if(str(request.user.id) != request.data['user'][0] and len(request.data['user']) == 1):
            return Response(status=400)
        return super().create(request, *args, **kwargs)
    
class StudentViewSet(ModelViewSet):
    queryset=Student.objects.all()
    serializer_class=StudentSerializer
class ProfViewSet(ModelViewSet):
    queryset=Professor.objects.all()
    serializer_class=ProfSerializer
class InterestViewSet(ModelViewSet):
    queryset=Interests.objects.all()
    serializer_class=InterestSerializer
class ApplicationViewSet(ModelViewSet):
    queryset=Application.objects.all()
    serializer_class=ApplicationSerializer
