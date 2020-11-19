from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name', 'email']
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = ['id', 'research_field']
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    class Meta:
        model = Student
        fields = ['id','user','bio','cgpa', 'interests','cv','transcript','pic']
class ProfSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)

    class Meta:
        model = Professor
        fields = ['id', 'user', 'dept', 'interests', 'webpage_link']
class ProjectSerializer(serializers.ModelSerializer):
    prof = ProfSerializer(many=False, read_only=True)
    class Meta:
        model = Project
        fields = ['id','prof','title','description','cpi','vacancy','min_year','duration','learning_outcome','prereq','selection_procedure','release_date','last_date']


class ApplicationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)
    project = ProjectSerializer(many=False, read_only=True)
    class Meta:
        model = Application
        fields = ['id', 'student', 'project', 'preference', 'cover_letter']
