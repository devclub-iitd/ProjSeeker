from django.shortcuts import render
from django.http.response import HttpResponse
from django.urls.base import reverse_lazy
from rest_framework.response import Response
from rest_framework.viewsets import *
from .models import *
from .serializers import *
from rest_framework.decorators import action

# Create your views here.
def index(request):
    return HttpResponse("Hello World!")


def dashboard(request):
    return render(request, 'dashboard.html')

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return render(request,template_name='project-detail.html', context={'project': serializer.data})

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
