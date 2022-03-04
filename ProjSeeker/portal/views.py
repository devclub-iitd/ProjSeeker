from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import *
from .models import *
from .serializers import *
from .filters import ProjectFilter
from rest_framework.decorators import action
from rest_framework import permissions, request
from django.contrib.auth.decorators import login_required, permission_required
from django_filters import rest_framework as filters
from django.contrib.auth import login, logout
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User, Group
import os
import requests
# Create your views here.


def index(request):
    return render(request, 'home.html')


def dashboard(request):
    return render(request, 'dashboard.html', context={'is_prof': isProf(request.user), 'is_student': isStudent(request.user)})


def iitd_redirect(request):

    return redirect(f'{os.environ.get("IITD_REDIRECT_URL")}?response_type=code&client_id={os.environ.get("CLIENT_ID")}&state=xyz')


def authenticate(request):

    def check_student_id(unique_iitd_id):
        return unique_iitd_id[:4].isnumeric()

    r = requests.post(os.environ.get("IITD_OAUTH_TOKEN_URL"), {'client_id': os.environ.get("CLIENT_ID"),
                                                               'client_secret': os.environ.get("CLIENT_SECRET"),
                                                               'grant_type': os.environ.get("AUTHORIZATION_CODE"),
                                                               'code': request.GET.get('code')})

    oauth_resp = r.json()
    if r.status_code != 200:
        print("An error occured in fetching token:\n %s" % oauth_resp)
        return HttpResponseForbidden()
    access_token = oauth_resp['access_token']
    print("Fetched access token: %s" % access_token)
    r = requests.post(os.environ.get("IITD_RESOURCE_URL"), {
        'access_token': access_token
    })
    profile_resp = r.json()
    if r.status_code != 200:
        print(
            "An error occured in fetching user details:\n %s" % profile_resp)
        return redirect(reverse('home'))
    try:
        email = profile_resp["email"]
        name = profile_resp["name"]
        uniqueiitdid = profile_resp["uniqueiitdid"]
        username = profile_resp["user_id"]
        dept = profile_resp["department"]
        degree = profile_resp["category"]

        student_dept = Departments.get_department_by_name(dept)
        student_degree = Degree.get_degree_by_name(degree)

        is_student = check_student_id(uniqueiitdid)
        existing_user = User.objects.filter(
            username=username, email=email)
        if existing_user.exists():
            login(request, existing_user[0])
        else:
            user = User.objects.create(
                username=username, email=email, first_name=name)
            user.set_password(get_random_string(32))
            user.save()
            if is_student:
                gp = Group.objects.get(name='student')
                Student.objects.create(
                    user=user, dept=student_dept, degree=student_degree)
            else:
                gp = Group.objects.get(name='prof')
                Professor.objects.create(user=user, dept=dept.upper())
            gp.user_set.add(user)
            login(request, user)

        return redirect(reverse('find-projects'))
    except Exception as e:
        print("Error occured in processing kerberos profile:\n %s" % e)
        return HttpResponseServerError()


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProjectFilter

    def update(self, request, *args, **kwargs):
        print(request.data)
        return super().update(request, *args, **kwargs)

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_prof'))
    def create(self, request, *args, **kwargs):
        print(request.data)
        kwargs['tags'] = request.data['tags']

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

        return render(request, template_name='project-detail.html', context={'project': serializer.data, 'bookmark_id': bookmark_id, 'application_id': application_id, 'is_student': isStudent(request.user)})

    def list(self, request, *args, **kwargs):
        qset = self.filter_queryset(queryset=self.get_queryset())
        serializer = self.get_serializer(qset, many=True)

        return Response(data={
            'projects': serializer.data,
            'is_prof': isProf(request.user),
        })

    @method_decorator(login_required)
    @ action(detail=False)
    def find_projects(self, request):
        return render(request, template_name="search-projects.html", context={'depts': Departments.choices, 'degrees': Degree.choices, 'types': Project.ProjectType.choices, 'durations': Project.Duration.choices})

    @ method_decorator(login_required)
    @ action(detail=False)
    def my_projects(self, request):
        qset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qset, many=True)

        if 'applied' in request.GET.keys() and request.GET['applied'] == 'true':
            return Response(data={
                'projects': serializer.data,
                'is_student': isStudent(request.user),
                'is_prof': isProf(request.user),
            })
        else:
            return render(request=request, template_name="dashboard.html", context={'projects': serializer.data, 'is_student': isStudent(request.user), 'is_prof': isProf(request.user)})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_student'))
    @ action(detail=False)
    def applied_projects(self, request):
        return render(request=request, template_name="applied-projects.html", context={'is_student': isStudent(request.user), 'is_prof': isProf(request.user)})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_prof'))
    @ action(detail=False, methods=['GET'])
    def create_new_project(self, request):
        return render(request, template_name="project-form.html", context={'project_types': Project.ProjectType.choices, 'degrees': Degree.choices, 'durations': Project.Duration.choices})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_student'))
    @ action(detail=True, methods=['GET'], url_name='apply-project', url_path='apply')
    def apply_for_project(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(project, many=False)

        return render(request, template_name='application-form.html', context={'project': serializer.data, 'isApplied': False})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_prof'))
    @ action(detail=True, methods=['GET'], url_name='edit-project', url_path='edit')
    def edit(self, request, pk=None):
        project = self.get_object()
        if(project.prof.user != request.user):
            return Response(403)
        serializer = self.get_serializer(project, many=False)

        interest_text = ', '.join([it['research_field']
                                  for it in serializer.data['tags']])

        return render(request, template_name='project-form.html', context={'project': serializer.data, 'project_types': Project.ProjectType.choices, 'degrees': Degree.choices, 'interest_text': interest_text, 'durations': Project.Duration.choices})


class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    @ method_decorator(permission_required('portal.is_student'))
    @ method_decorator(login_required)
    def create(self, request, *args, **kwargs):

        request.data._mutable = True
        request.data['user'] = request.user.id
        project_id = request.data['project'][0]

        if Bookmark.objects.filter(user__id=request.user.id, project__id=project_id).exists():
            return Response(status=400)

        return super().create(request, *args, **kwargs)


@ login_required
def get_uploaded_file(request, pk, file_name):
    user = request.user
    if user.id != pk or file_name not in ['cv.pdf', 'transcript.pdf', 'pic.jpg']:
        raise PermissionDenied()
    response = HttpResponse()
    response['X-Accel-Redirect'] = f'/protected/user_{pk}/{file_name}'
    return response


# TODO Refactor Student and Professor view sets and serializer code


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if(obj.user.id != request.user.id):
            self.permission_denied(
                request, message='Unauthorized User', code=403)
        return super().check_object_permissions(request, obj)

    def update(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().update(request, *args, **kwargs)

    @ action(detail=False, methods=['POST'])
    def delete_file(self, request):
        student = request.user.student_set.all()[0]

        file_type = request.data['type']
        if file_type not in Student.get_docs():
            return Response(400)
        getattr(student, file_type).delete()
        return Response(200)

    @ action(detail=False, methods=['GET'])
    def profile(self, request):
        user_id = request.GET.get('id', request.user.id)
        user = get_object_or_404(User, id=user_id)
        is_self_profile = (user == request.user)
        print(user, is_self_profile)

        student = user.student_set.all()[0]

        serializer = self.get_serializer(student, many=False)
        interest_text = ', '.join([it['research_field']
                                   for it in serializer.data['interests']])
        return render(request, template_name='profile.html', context={'user_data': serializer.data, 'interest_text': interest_text, 'is_student': isStudent(request.user), 'is_prof': isProf(request.user), 'is_self_profile': is_self_profile})

    @ action(detail=False, methods=['POST'])
    def check_documents(self, request):
        user = request.user
        student = user.student_set.all()[0]
        valid = False
        try:
            valid &= hasattr(student.cv, 'file')
            valid &= hasattr(student.transcript, 'file')

            if student.degree == Degree.phd:
                valid &= hasattr(student.noc, 'file')

            if valid:
                return Response(200)

        except:
            pass

        return Response(status=401, data={
            "err": True,
            "msg": "Please upload your documents before applying for a project"
        })


class ProfViewSet(ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if(obj.user.id != request.user.id):
            self.permission_denied(
                request, message='Unauthorized User', code=403)
        return super().check_object_permissions(request, obj)

    def update(self, request, *args, **kwargs):

        request.data._mutable = True
        return super().update(request, *args, **kwargs)

    @ action(detail=False, methods=['POST'])
    def delete_file(self, request):
        prof = request.user.professor_set.all()[0]

        file_type = request.data['type']
        if file_type not in Professor.get_docs():
            return Response(400)
        getattr(prof, file_type).delete()
        return Response(200)

    @ action(detail=False, methods=['GET'])
    def profile(self, request):
        user = request.user
        prof = user.professor_set.all()[0]

        serializer = self.get_serializer(prof, many=False)
        interest_text = ', '.join([it['research_field']
                                   for it in serializer.data['interests']])
        return render(request, template_name='profile.html', context={'user_data': serializer.data, 'interest_text': interest_text, 'is_student': isStudent(request.user), 'is_prof': isProf(request.user)})


class InterestViewSet(ModelViewSet):
    queryset = Interests.objects.all()
    serializer_class = InterestSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = {
        'research_field': ['startswith']
    }


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = ['status']

    def check_object_permissions(self, request, obj):
        if(obj.student.user.id != request.user.id and obj.project.prof.user.id != request.user.id):
            self.permission_denied(request, message='Forbidden', code=403)
        if request.method != 'GET' and obj.project.deadline_passed() and isStudent(request.user):
            self.permission_denied(
                request, message='Deadline Passed!', code=400)
        return super().check_object_permissions(request, obj)

    @ action(detail=False)
    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_prof'))
    def list_received_applications(self, request):
        user = request.user
        applications = Application.objects.filter(project__prof__user=user)
        applications = self.filter_queryset(applications)

        serializer = self.get_serializer(applications, many=True)
        data = serializer.data
        for appl in data:
            appl['project_title'] = Project.objects.get(
                id=appl['project']).title
            stud_user = Student.objects.get(id=appl['student']).user
            appl['student_name'] = stud_user.first_name + \
                " " + stud_user.last_name

        return Response({'applications': data, 'is_student': isStudent(request.user), 'is_prof': isProf(request.user)})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_prof'))
    @ action(detail=False)
    def view_received_applications(self, request):
        return render(request=request, template_name='application-card.html', context={'is_prof': isProf(request.user), 'is_student': isStudent(request.user)})

    @ method_decorator(login_required)
    @ method_decorator(permission_required('portal.is_student'))
    def create(self, request, *args, **kwargs):
        student = Student.objects.get(user__id=request.user.id)
        request.data._mutable = True
        request.data['student'] = student.id
        request.data['status'] = Status.in_review

        project = Project.objects.get(id=int(request.data['project']))
        if project is None or project.deadline_passed():
            self.permission_denied(
                request, message='Deadline Passed', code=400)

        return super().create(request, *args, **kwargs)

    @ method_decorator(login_required)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        project_data = ProjectSerializer(Project.objects.get(
            id=instance.project.id), many=False).data
        serializer = self.get_serializer(instance, many=False)
        student_name = f'{instance.student.user.first_name} {instance.student.user.last_name}'

        return render(request, template_name='application-form.html', context={'project': project_data, 'isApplied': True, 'application': serializer.data, 'is_prof': isProf(request.user), 'status_choices': Status, 'student_user_id': instance.student.user.id, 'student_name': student_name})

    @ method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data._mutable = True
        request.data['project'] = instance.project.id
        request.data['student'] = instance.student.id
        return super().update(request, *args, **kwargs)
