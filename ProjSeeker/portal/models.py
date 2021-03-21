from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from .storage import OverwriteStorage
from multiselectfield import MultiSelectField


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


class Student(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    bio = models.TextField()
    cv = models.FileField(_("Resume"), upload_to= upload_cv,storage=OverwriteStorage(), null=True)
    transcript = models.FileField(_("Transcripts"), upload_to= upload_transcript , storage=OverwriteStorage(), null=True)
    pic = models.FileField(_("Profile Pic"), upload_to=upload_pic, null=True, storage=OverwriteStorage())
    cgpa = models.FloatField(_("CGPA"), validators=[MaxValueValidator(10)], null=True)
    interests = models.ManyToManyField("Interests")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Interests(models.Model):
    research_field = models.CharField(_("Research Area of Interest"), max_length=50)

    def __str__(self):
        return self.research_field

    @staticmethod
    def to_choices():
        interests = Interests.objects.all()
        return [(intr.research_field, intr.research_field) for intr in interests]
    

class Professor(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    dept = models.CharField(_("department"), max_length=50, choices=Departments.choices)
    interests = models.ManyToManyField("Interests")
    webpage_link = models.URLField(_("Webpage Link"), max_length=200, null=True)
    pic = models.FileField(_("Profile Pic"), upload_to=upload_pic, storage=OverwriteStorage(), null=True)
    bio = models.TextField(_("Biography"), null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} @ {self.dept}'
    

class Project(models.Model):

    class Category(models.TextChoices):
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
    cpi = models.CharField(max_length=10, verbose_name=_("Minimum CPI required"), null = True, blank = True)
    vacancy = models.PositiveSmallIntegerField()
    min_year = models.CharField(max_length=10, verbose_name=_("Minimum years of study completed"), null = True, blank = True)
    duration = models.CharField(max_length=50, choices=Category.choices ,null = True, blank = True)
    learning_outcome = models.TextField()
    prereq = models.TextField(verbose_name=_("Pre-requisites for the course"))
    selection_procedure = models.TextField()
    tags = models.ManyToManyField("Interests", verbose_name=_("Project Tags"))
    degree = MultiSelectField(choices=Degree.choices, null=True, blank=True)
    project_type = MultiSelectField(choices=Duration.choices, null=True, blank=True)
    is_paid = models.BooleanField(_("Funding available?"), default=False)
    # TODO run validation based on these data and times
    release_date = models.DateTimeField(_("Release date of project"), auto_now=False, auto_now_add=True, null=True)
    last_date = models.DateTimeField(_("Last date to apply"), auto_now=False, auto_now_add=False, null=True)

    def __str__(self):
        return f'{self.title} | {self.prof}'
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} -> {self.project}'
    
    
class Application(models.Model):
    student = models.ForeignKey("Student", verbose_name=_("Student"), on_delete=models.CASCADE)
    project = models.ForeignKey("Project", verbose_name=_("Project applied to"), on_delete=models.CASCADE)
    preference = models.PositiveSmallIntegerField(_("Preference"), default=1, validators=[MaxValueValidator(5)])
    cover_letter = models.TextField(_("Cover letter for the application"))
    experience = models.TextField(_("Relevant Experience"))
    status = models.CharField(_("Accepted status"), max_length=50, choices=Status.choices, default=Status.in_review)
    remark = models.TextField(_("Rejection Remark"), default="")

    def __str__(self):
        return f'{self.student} | {self.project}'