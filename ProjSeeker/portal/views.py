from django.db.models.query_utils import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
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
    return render(request, 'home.html')


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

    search = filters.filters.CharFilter(method='search_project')
    applied = filters.filters.BooleanFilter(method='filter_applied')
    bookmarked = filters.filters.BooleanFilter(method='filter_bookmarked')
    floated = filters.filters.BooleanFilter(method='filter_floated')
    status = filters.filters.ChoiceFilter(choices=Status.choices, method='filter_appl_status')
    is_paid = filters.filters.BooleanFilter(field_name='is_paid')
    
    prof__dept = filters.filters.MultipleChoiceFilter(choices=Departments.choices)
    degree__icontains = filters.filters.MultipleChoiceFilter(choices=Degree.choices)
    project_type__icontains = filters.filters.MultipleChoiceFilter(choices=Project.Category.choices)
    duration__icontains = filters.filters.MultipleChoiceFilter(choices=Project.Duration.choices)
    tags__research_field = filters.filters.MultipleChoiceFilter(choices=Interests.to_choices())

    def search_project(self, queryset, name, value):
        q = Q(title__icontains=value)
        q |= Q(description__icontains=value)
        q |= Q(prof__user__first_name__icontains=value)
        q |= Q(prof__user__last_name__icontains=value)
        try:
            return Project.objects.filter(q)
        except:
            return Project.objects.none()

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


# TODO handle security of all endpoints!! -> Prof/User access control
class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProjectFilter    

    def update(self, request, *args, **kwargs):
        print(request.data)
        return super().update(request, *args, **kwargs)

    # NOTE: Prof Only
    @method_decorator(login_required)
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

        bookmark_id = None
        application_id = None

        if request.user.is_authenticated:
            bmk = Bookmark.objects.filter(user=request.user, project=instance)
            if bmk.exists():
                bookmark_id = bmk[0].id
            
            appl = instance.application_set.all().filter(student__user=request.user)
            if appl.exists():
                application_id = appl[0].id

        return render(request,template_name='project-detail.html', context={'project': serializer.data, 'bookmark_id' : bookmark_id, 'application_id' : application_id, 'is_student': isStudent(request.user)})

    def list(self, request, *args, **kwargs):
        qset = self.filter_queryset(queryset=self.get_queryset())
        serializer = self.get_serializer(qset, many=True)

        return Response(data={
            'projects' : serializer.data,
            'is_prof' : isProf(request.user),
        })

    @action(detail=False)
    def find_projects(self,request):
        return render(request, template_name="search-projects.html", context={'depts': Departments.choices, 'degrees': Degree.choices, 'types': Project.Category.choices, 'durations': Project.Duration.choices })

    @method_decorator(login_required)
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
    
    @method_decorator(login_required)
    @action(detail=False)
    def applied_projects(self, request):
        return render(request=request, template_name="applied-projects.html", context={'is_student': isStudent(request.user), 'is_prof' : isProf(request.user)})
        
    # NOTE: Prof only
    @method_decorator(login_required)
    @action(detail=False, methods=['GET'])
    def create_new_project(self, request):
        if(not isProf(request.user)):
            return Response(status=403)
        return render(request, template_name="project-form.html", context={'project_types' : Project.Category.choices, 'degrees': Degree.choices})

    # NOTE: student only
    @method_decorator(login_required)
    @action(detail=True, methods=['GET'],url_name='apply-project',url_path='apply')
    def apply_for_project(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(project, many=False)
        
        return render(request, template_name='application-form.html',context={'project' : serializer.data, 'isApplied': False})

    # NOTE: prof only
    @method_decorator(login_required)
    @action(detail=True, methods=['GET'],url_name='edit-project', url_path='edit')
    def edit(self, request, pk=None):
        project = self.get_object()
        if(project.prof.user != request.user):
            return Response(403)
        serializer = self.get_serializer(project, many=False)
        
        interest_text = ', '.join([it['research_field'] for it in serializer.data['tags']])

        return render(request, template_name='project-form.html',context={'project' : serializer.data, 'project_types' : Project.Category.choices, 'degrees': Degree.choices, 'interest_text': interest_text})
class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    # NOTE: student only
    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        if not isStudent(request.user):
            return Response(403)
        
        request.data._mutable = True
        request.data['user'] = request.user.id
        project_id = request.data['project'][0]

        if Bookmark.objects.filter(user__id=request.user.id, project__id=project_id).exists():
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

    # NOTE: Prof only
    @action(detail=False)
    @method_decorator(login_required)
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

    # NOTE: Prof only
    @method_decorator(login_required)
    @action(detail=False)
    def view_received_applications(self, request):
        return render(request=request, template_name='application-card.html', context={'is_prof': isProf(request.user), 'is_student': isStudent(request.user)})
    
    # NOTE: Student only
    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        student = Student.objects.get(user__id=request.user.id)
        request.data._mutable = True
        request.data['student'] = student.id
        request.data['status'] = Status.in_review
        return super().create(request, *args, **kwargs)

    @method_decorator(login_required)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        project_data = ProjectSerializer(Project.objects.get(id=instance.project.id),many=False).data
        serializer = self.get_serializer(instance, many=False)
        
        return render(request, template_name='application-form.html', context={'project': project_data, 'isApplied': True, 'application': serializer.data, 'is_prof': isProf(request.user), 'status_choices' : Status, 'student_user_id': instance.student.user.id})

    # NOTE: Student only
    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data._mutable = True
        request.data['project'] = instance.project.id
        request.data['student'] = instance.student.id
        return super().update(request, *args, **kwargs)
    