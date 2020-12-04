from rest_framework import serializers
from rest_framework.fields import ChoiceField, DateTimeField
from .models import *

class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)

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
    dept = ChoiceField(choices=Departments.choices)
    class Meta:
        model = Professor
        fields = ['id', 'user', 'dept', 'interests', 'webpage_link']
class ProjectSerializer(serializers.ModelSerializer):
    prof = ProfSerializer(many=False, read_only=True)
    release_date = DateTimeField(format="%c")
    last_date = DateTimeField(format="%c")
    class Meta:
        model = Project
        fields = ['id','prof','title','description','cpi','vacancy','min_year','duration','learning_outcome','prereq','selection_procedure','release_date','last_date']

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'student', 'project', 'preference', 'cover_letter', 'experience']