from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from .storage import OverwriteStorage
from multiselectfield import MultiSelectField

def isStudent(user):
    return user.has_perm('portal.is_student')


def isProf(user):
    return user.has_perm('portal.is_prof')

# Create your models here.


class Departments(models.TextChoices):
    CSE = 'CSE', _('Computer Science and Engineering')
    EE = 'EE', _('Electrical Engineering')
    ME = 'ME', _('Mechanical Engineering')
    CH = 'CH', _('Chemical Engineering')
    CE = 'CE', _('Civil Engineering')
    BB = 'BB', _('Biotech Engineering')
    TT = 'TT', _('Textile Engineering')
    PH = 'PH', _('Engineering Physics')
    MT = 'MT', _('Mathematics')


class Status(models.TextChoices):
    in_review = 'IR', _('In Review')
    on_hold = 'OH', _('On Hold')
    accepted = 'AC', _('Accepted')
    rejected = 'RE', _('Rejected')


class Degree(models.TextChoices):
    btech = 'BTech', _('BTech')
    mtech = 'MTech', _('MTech')
    dual = 'Dual', _('Dual')
    phd = 'PhD', _('PhD')


def upload_handler(student, filename):
    print('user_{0}/{1}'.format(student.user.id, filename))
    return 'user_{0}/{1}'.format(student.user.id, filename)


def upload_pic(s, _): return upload_handler(s, 'pic.jpg')
def upload_cv(s, _): return upload_handler(s, 'cv.pdf')
def upload_transcript(s, _): return upload_handler(s, 'transcript.pdf')
def upload_noc(s, _): return upload_handler(s, 'noc.pdf')


class Student(models.Model):
    user = models.ForeignKey(User, verbose_name=_(
        "Auth User"), on_delete=models.CASCADE)
    bio = models.TextField()
    degree = models.CharField(
        _("Degree"), choices=Degree.choices, max_length=50)
    cv = models.FileField(_("Resume"), upload_to=upload_cv,
                          storage=OverwriteStorage(), null=True)
    transcript = models.FileField(
        _("Transcripts"), upload_to=upload_transcript, storage=OverwriteStorage(), null=True)
    pic = models.FileField(
        _("Profile Pic"), upload_to=upload_pic, null=True, storage=OverwriteStorage(), blank=True)
    noc = models.FileField(
        _("NOC"), upload_to=upload_noc, null=True, storage=OverwriteStorage(), blank=True)
    cgpa = models.FloatField(_("CGPA"), validators=[
                             MaxValueValidator(10)], null=True)
    interests = models.ManyToManyField("Interests")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @staticmethod
    def get_docs():
        return ['transcript', 'cv', 'pic', 'noc']
    
    def degree_verbose(self):
        return dict(Degree)[self.degree]

    class Meta:
        permissions = (('is_student', 'Is Student'),)


class Interests(models.Model):
    research_field = models.CharField(
        _("Research Area of Interest"), max_length=50)

    def __str__(self):
        return self.research_field

    @staticmethod
    def to_choices():
        interests = Interests.objects.all()
        return [(intr.research_field, intr.research_field) for intr in interests]


class Professor(models.Model):
    user = models.ForeignKey(User, verbose_name=_(
        "Auth User"), on_delete=models.CASCADE)
    dept = models.CharField(_("department"), max_length=50,
                            choices=Departments.choices)
    interests = models.ManyToManyField("Interests")
    webpage_link = models.URLField(
        _("Webpage Link"), max_length=200, null=True)
    pic = models.FileField(
        _("Profile Pic"), upload_to=upload_pic, storage=OverwriteStorage(), null=True)
    bio = models.TextField(_("Biography"), null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} @ {self.dept}'

    @staticmethod
    def get_docs():
        return ['pic']

    class Meta:
        permissions = (('is_prof', 'Is Prof'),)


class Project(models.Model):

    class Category(models.TextChoices):
        ai_ml = 'ai_ml', _(
            'Artificial Intelligence (AI) and Machine Learning (ML)')
        nlp = 'NLP', _('Natural Language Processing')
        da = 'data analysis', _('Databases and Data Analytics')
        algo = 'algos', _('Algorithms and Complexity Theory')
        arch = 'architecture', _('Architecture and Embedded Systems')
        vision = 'vision', _('Computer Graphics/Vision')
        networks = 'networks', _('Computer Networks and Distributed Systems')
        pl = 'prog lang', _(
            'Programming Languages, Semantics and Verification')
        os = 'os', _(
            'Operating Systems, High Performance Computing and Systems Software')
        ict = 'ict', _(
            'Information and Communication Technologies for Development')
        neuro = 'neuro', _('Neuroinformatics and Medical informatics')
        cybersec = 'cyber security', _(
            'Cyber Security and Secure Information Systems')

        other = 'other', _('Other')

    class ProjectType(models.TextChoices):
        disa = 'DISA', _('DISA')
        sura = 'SURA', _('SURA')
        major = 'Major Project', _('Major Project')
        minor = 'Minor Project', _('Minor Project')
        design = 'Design Project', _('Design Project')

    class Duration(models.TextChoices):
        summer = 'summer', _('Summer Long')
        winter = 'winter', _('Winter Long')
        semester = 'semester', _('Semester Long')
        year = 'year', _('Year Long')
        short = 'short', _('Short Term')
        long = 'long', _('Long Term')
        other = 'other', _('Other')

    prof = models.ForeignKey("Professor",  on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    cpi = models.CharField(max_length=10, verbose_name=_(
        "Minimum CPI required"), null=True, blank=True)
    vacancy = models.PositiveSmallIntegerField()
    min_year = models.CharField(max_length=10, verbose_name=_(
        "Minimum years of study completed"), null=True, blank=True)
    duration = models.CharField(
        max_length=50, choices=Duration.choices, null=True, blank=True)
    learning_outcome = models.TextField()
    prereq = models.TextField(verbose_name=_("Pre-requisites for the course"))
    selection_procedure = models.TextField()
    category = models.CharField(
        _("Project Category"), choices=Category.choices, max_length=200)
    tags = models.ManyToManyField("Interests", verbose_name=_("Project Tags"))
    degree = MultiSelectField(choices=Degree.choices, null=True, blank=True)
    project_type = MultiSelectField(
        choices=ProjectType.choices, null=True, blank=True)
    is_paid = models.BooleanField(_("Funding available?"), default=False)
    release_date = models.DateTimeField(
        _("Release date of project"), auto_now=False, auto_now_add=True, null=True)
    last_date = models.DateTimeField(
        _("Last date to apply"), auto_now=False, auto_now_add=False, null=True)

    def __str__(self):
        return f'{self.title} | {self.prof}'

    def deadline_passed(self) -> bool:
        from datetime import datetime as dt
        from pytz import UTC as utc
        return self.last_date < utc.localize(dt.now())


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} -> {self.project}'


class Application(models.Model):
    student = models.ForeignKey("Student", verbose_name=_(
        "Student"), on_delete=models.CASCADE)
    project = models.ForeignKey("Project", verbose_name=_(
        "Project applied to"), on_delete=models.CASCADE)
    preference = models.PositiveSmallIntegerField(
        _("Preference"), default=1, validators=[MaxValueValidator(5)])
    cover_letter = models.TextField(_("Cover letter for the application"))
    experience = models.TextField(_("Relevant Experience"))
    status = models.CharField(_("Accepted status"), max_length=50,
                              choices=Status.choices, default=Status.in_review)
    remark = models.TextField(_("Rejection Remark"), default="")

    def __str__(self):
        return f'{self.student} | {self.project}'
