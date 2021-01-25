from django.shortcuts import render
from django.http.response import HttpResponse
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import *
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework import permissions, request
from django.contrib.auth.decorators import login_required
from django_filters import rest_framework as filters



# Create your views here.
def index(request):
    return render(request, 'home.html');


def dashboard(request):
    return render(request, 'dashboard.html', context={'is_prof': isProf(request.user), 'is_student': isStudent(request.user)})

def isStudent(user):
    if( not user.is_authenticated):
        return False
    return len(user.student_set.all()) == 1

def isProf(user):
    if( not user.is_authenticated):
        return False
    return len(user.professor_set.all()) == 1

class ProjectFilter(filters.FilterSet):

    title__icontains = filters.filters.CharFilter(field_name='title', lookup_expr='icontains')
    prof__dept = filters.filters.MultipleChoiceFilter(choices=Departments.choices)
    applied = filters.filters.BooleanFilter(method='filter_applied')
    bookmarked = filters.filters.BooleanFilter(method='filter_bookmarked')
    floated = filters.filters.BooleanFilter(method='filter_floated')
    status = filters.filters.ChoiceFilter(choices=Status.choices, method='filter_appl_status')

    def filter_applied(self, queryset, name, value):
        try:
            user = self.request.user
            assert isStudent(user)

            applied = Application.objects.select_related('project').filter(student__user=user)
            pids = [appl.project.id for appl in applied]

            return Project.objects.filter(id__in=pids)
        except:
            return Project.objects.none()

    def filter_bookmarked(self, queryset, name, value):
        try:
            user = self.request.user
            # assert isStudent(user)

            bookmarked = Bookmark.objects.filter(user=user)
            pids = [bmk.project.id for bmk in bookmarked]

            return Project.objects.filter(id__in=pids)
        except:
            return Project.objects.none()
    
    def filter_floated(self, queryset, name, value):
        try:
            user = self.request.user
            assert isProf(user)

            return Project.objects.filter(prof__user=user)
        except:
            return Project.objects.none()
    
    def filter_appl_status(self, queryset, name, value):
        try:
            user = self.request.user

            appls = Application.objects.filter(student__user=user,status=value)
            pids = [appl.project.id for appl in appls]

            return Project.objects.filter(id__in=pids)
        except:
            return Project.objects.none()

    class Meta:
        model = Project
        fields = ['title', 'prof']


# TODO handle security of all endpoints!!
class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProjectFilter    

    def create(self, request, *args, **kwargs):
        if(not isProf(request.user)):
            return Response(403)
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        kwargs['prof'] = Professor.objects.get(user=request.user)
        serializer.save(*args, **kwargs)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        bookmark = { 'is_bmkd': False, 'bmk': None } 
        if (request.user.is_authenticated):
            bmk = Bookmark.objects.filter(user=request.user).filter(project=instance)
            bookmark['is_bmkd'] = len(bmk) != 0
            bookmark['bmk'] = bmk[0] if (bookmark['is_bmkd']) else None

        applications = instance.application_set.all().filter(student__user=request.user) if (isStudent(request.user))  else []
        isApplied = False
        if(len(applications) >= 1):
            isApplied = True
        return render(request,template_name='project-detail.html', context={'project': serializer.data, 'bookmark' : bookmark, 'isApplied': isApplied, 'appId' : applications[0].id if(isApplied) else None})

    def list(self, request, *args, **kwargs):
        qset = self.filter_queryset(queryset=self.get_queryset())
        serializer = self.get_serializer(qset, many=True)

        return Response(data={
            'projects' : serializer.data,
            'is_prof' : isProf(request.user),
        })

    @action(detail=False)
    def find_projects(self,request):
        return render(request, template_name="search-projects.html", context={'depts': Departments.choices})

    @action(detail=False)
    def my_projects(self, request):
        qset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qset, many=True)
        
        if 'applied' in request.GET.keys() and request.GET['applied'] == 'true':
            return Response(data={
                'projects' : serializer.data,
                'is_student': isStudent(request.user),
                'is_prof': isProf(request.user),
            })
        else:
            return render(request=request, template_name="dashboard.html", context={'projects' : serializer.data,'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})
    
    @action(detail=False)
    def applied_projects(self, request):
        return render(request=request, template_name="applied-projects.html", context={'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})
        

    @action(detail=False, methods=['GET'])
    def create_new_project(self, request):
        if(not isProf(request.user)):
            return Response(status=403)
        return render(request, template_name="project-form.html")

    @method_decorator(login_required)
    @action(detail=True, methods=['GET'],url_name='apply-project',url_path='apply')
    def apply_for_project(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(project, many=False)
        
        return render(request, template_name='application-form.html',context={'project' : serializer.data, 'isApplied': False})

    @method_decorator(login_required)
    @action(detail=True, methods=['GET'],url_name='edit-project', url_path='edit')
    def edit(self, request, pk=None):
        project = self.get_object()
        if(project.prof.user != request.user):
            return Response(403)
        serializer = self.get_serializer(project, many=False)

        return render(request, template_name='project-form.html',context={'project' : serializer.data})
class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if(str(request.user.id) != request.data['user'][0] and len(request.data['user']) == 1 and len(request.data['project']) == 1):
            return Response(status=400)
        print(request.data)
        if(len(Bookmark.objects.filter(user__id=request.user.id).filter(project__id=request.data['project'][0])) > 0):
            return Response(status=400)
        return super().create(request, *args, **kwargs)

# TODO Refactor Student and Professor view sets and serializer code
class StudentViewSet(ModelViewSet):
    queryset=Student.objects.all()
    serializer_class=StudentSerializer
    permission_classes=[permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if(obj.user.id != request.user.id):
            raise Exception("Unauthorized user")
        return super().check_object_permissions(request, obj)

    def update(self, request, *args, **kwargs):
        print(request.data)
        request.data._mutable = True
        if(not request.data['transcript']):
            del request.data['transcript']
        if(not request.data['cv']):
            del request.data['cv']
        if(not request.data['pic']):
            del request.data['pic']
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def delete_file(self, request):
        student = request.user.student_set.all()
        if(len(student) != 1):
            return Response(403)
        student = student[0]
        if(student.user.id != request.user.id):
            return Response(403)

        print(request.data)

        file_type = request.data['type']
        print(file_type)
        if(file_type == 'pic'):
            student.pic.delete()
        elif(file_type == 'cv'):
            student.cv.delete()
        elif(file_type == 'transcript'):
            student.transcript.delete()
        return Response(200)

    @action(detail=False,methods=['GET'])
    def profile(self, request):
        user = request.user
        students = user.student_set.all()

        if(len(students) == 1):
            student = students[0]
            serializer = self.get_serializer(student, many=False)
            interest_text = ', '.join([it['research_field'] for it in serializer.data['interests']])
            return render(request, template_name='profile.html', context={'user_data':serializer.data, 'interest_text': interest_text, 'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})
        return Response(404)
    
class ProfViewSet(ModelViewSet):
    queryset=Professor.objects.all()
    serializer_class=ProfSerializer
    permission_classes=[permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if(obj.user.id != request.user.id):
            raise Exception("Unauthorized user")
        return super().check_object_permissions(request, obj)

    def update(self, request, *args, **kwargs):
        
        request.data._mutable = True
        if(not request.data['pic']):
            del request.data['pic']

        instance = self.get_object()
        for dept in Departments.choices:
            if(instance.dept == dept[0]):
                request.data['dept'] = dept[1]

        print(request.data)
        
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def delete_file(self, request):
        prof = request.user.professor_set.all()
        if(len(prof) != 1):
            return Response(403)
        prof = prof[0]
        if(prof.user.id != request.user.id):
            return Response(403)

        print(request.data)

        file_type = request.data['type']
        print(file_type)
        if(file_type == 'pic'):
            prof.pic.delete()
        return Response(200)

    @action(detail=False,methods=['GET'])
    def profile(self, request):
        user = request.user
        professors = user.professor_set.all()

        if(len(professors) == 1):
            prof = professors[0]
            serializer = self.get_serializer(prof, many=False)
            interest_text = ', '.join([it['research_field'] for it in serializer.data['interests']])
            return render(request, template_name='profile.html', context={'user_data':serializer.data, 'interest_text': interest_text, 'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})
        return Response(404)
    
class InterestViewSet(ModelViewSet):
    queryset=Interests.objects.all()
    serializer_class=InterestSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = {
        'research_field': ['startswith']
    }
class ApplicationViewSet(ModelViewSet):
    queryset=Application.objects.all()
    serializer_class=ApplicationSerializer
    permission_classes=[permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = ['status']

    def check_object_permissions(self, request, obj):
        if(obj.student.user.id != request.user.id and obj.project.prof.user.id != request.user.id):
            raise Exception("Forbidden")
        return super().check_object_permissions(request, obj)

    @action(detail=False)
    def list_received_applications(self, request):
        user = request.user
        if(not isProf(user)):
            return Response(403)
        applications = Application.objects.filter(project__prof__user=user)

        applications = self.filter_queryset(applications)

        serializer = self.get_serializer(applications, many=True)
        data = serializer.data
        for appl in data:
            appl['project_title'] = Project.objects.get(id=appl['project']).title
            stud_user = Student.objects.get(id=appl['student']).user
            appl['student_name'] = stud_user.first_name + " " + stud_user.last_name
        
        return Response({'applications': data, 'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})

    @action(detail=False)
    def view_received_applications(self, request):
        return render(request=request, template_name='application-card.html', context={'is_prof': isProf(request.user), 'is_student': isStudent(request.user)})
    
    def create(self, request, *args, **kwargs):
        students = Student.objects.filter(user__id=request.user.id)
        if(len(students) != 1):
            return Response(status=403)
        request.data._mutable = True
        request.data['student'] = students[0].id
        request.data['status'] = Status.in_review
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        project_data = ProjectSerializer(Project.objects.get(id=instance.project.id),many=False).data
        serializer = self.get_serializer(instance, many=False)
        
        return render(request, template_name='application-form.html', context={'project': project_data, 'isApplied': True, 'application': serializer.data, 'is_prof': isProf(request.user), 'status_choices' : Status})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data._mutable = True
        request.data['project'] = instance.project.id
        request.data['student'] = instance.student.id
        return super().update(request, *args, **kwargs)
    