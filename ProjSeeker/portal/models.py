from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

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


def upload_handler(student, filename):
    return 'user_{0}/{1}'.format(student.user.id, filename)


def upload_cv(s, _): return upload_handler(s, 'cv.pdf')
def upload_transcript(s, _): return upload_handler(s, 'transcript.pdf')


class Student(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    bio = models.TextField()
    cv = models.FileField(_("Resume"), upload_to= upload_cv, max_length=100, null=True)
    transcript = models.FileField(_("Transcripts"), upload_to= upload_transcript , max_length=100, null=True)
    pic = models.FileField(_("Profile Pic"), upload_to=upload_handler, max_length=100, null=True)
    cgpa = models.FloatField(_("CGPA"), validators=[MaxValueValidator(10)], null=True)
    interests = models.ManyToManyField("Interests")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Interests(models.Model):
    research_field = models.CharField(_("Research Area of Interest"), max_length=50)

    def __str__(self):
        return self.research_field
    

class Professor(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    dept = models.CharField(_("department"), max_length=50, choices=Departments.choices)
    interests = models.ManyToManyField("Interests")
    webpage_link = models.URLField(_("Webpage Link"), max_length=200, null=True)
    pic = models.FileField(_("Profile Pic"), upload_to=upload_handler, max_length=100, null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} @ {self.dept}'
    

class Project(models.Model):
    prof = models.ForeignKey("Professor",  on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    cpi = models.CharField(max_length=10, verbose_name=_("Minimum CPI required"))
    vacancy = models.PositiveSmallIntegerField()
    min_year = models.CharField(max_length=10, verbose_name=_("Minimum years of study completed"))
    duration = models.CharField(max_length=50)
    learning_outcome = models.TextField()
    prereq = models.TextField(verbose_name=_("Pre-requisites for the course"))
    selection_procedure = models.TextField()
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

    def __str__(self):
        return f'{self.student} | {self.project}'