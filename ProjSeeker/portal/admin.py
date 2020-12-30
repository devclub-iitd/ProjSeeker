from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'cgpa', 'bio']
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['user', 'dept']
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'project', 'preference', 'status']
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['prof', 'title']
@admin.register(Interests)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['research_field']
@admin.register(Bookmark)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['user', 'project']

