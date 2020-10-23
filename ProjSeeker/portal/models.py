from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
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


def upload_path_handler(student, filename):
    return 'user_{0}/{1}'.format(student.user.id, filename)

class Student(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    bio = models.TextField()
    cv = models.FileField(_("Resume"), upload_to=upload_path_handler, max_length=100)

    

class Professor(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Auth User"), on_delete=models.CASCADE)
    dept = models.CharField(_("department"), max_length=50, choices=Departments.choices)

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

    
class Application(models.Model):
    student = models.ForeignKey("Student", verbose_name=_("Student"), on_delete=models.CASCADE)
    project = models.ForeignKey("Project", verbose_name=_("Project applied to"), on_delete=models.CASCADE)
    preference = models.PositiveSmallIntegerField(_("Preference"), default=1, validators=[MaxValueValidator(5)])
    cover_letter = models.TextField(_("Cover letter for the application"))

