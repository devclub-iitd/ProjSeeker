from rest_framework import serializers
from rest_framework.fields import ChoiceField, DateTimeField
from .models import *


def process_interests(interests_text, obj):
    obj.clear()
    new_interests = interests_text.split(', ')

    for text in new_interests:
        if text == '':
            continue
        try:
            existing_interest = Interests.objects.get(research_field=text)
            obj.add(existing_interest)
        except:
            new_intr = Interests.objects.create(research_field=text)
            obj.add(new_intr)


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
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = ['id', 'research_field']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    dept = ChoiceField(choices=Departments.choices,
                       allow_blank=True, read_only=True)
    degree = ChoiceField(choices=Degree.choices,
                         allow_blank=True, read_only=True)
    pic = serializers.FileField(required=False)
    cv = serializers.FileField(required=False)
    noc = serializers.FileField(required=False)

    class Meta:
        model = Student
        fields = ['id', 'user', 'bio', 'cgpa', 'interests',
                  'cv', 'transcript', 'pic', 'degree', 'dept', 'noc']

    def is_valid(self, raise_exception):

        interests_text = self.initial_data['interests']
        del self.initial_data['interests']
        ret_val = super().is_valid(raise_exception=raise_exception)

        process_interests(interests_text=interests_text,
                          obj=self.instance.interests)

        return ret_val


class ProfSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    dept = ChoiceField(choices=Departments.choices, read_only=True)
    pic = serializers.FileField(required=False)

    def is_valid(self, raise_exception):
        interests_text = self.initial_data['interests']
        del self.initial_data['interests']
        ret_val = super().is_valid(raise_exception=raise_exception)

        process_interests(interests_text=interests_text,
                          obj=self.instance.interests)

        return ret_val

    class Meta:
        model = Professor
        fields = ['id', 'user', 'dept', 'interests',
                  'webpage_link', 'bio', 'pic']


class ProjectSerializer(serializers.ModelSerializer):
    prof = ProfSerializer(many=False, read_only=True)
    release_date = DateTimeField(format="%c", required=False)
    last_date = DateTimeField(format="%c", required=False)
    tags = InterestSerializer(many=True, read_only=True)
    degree = serializers.MultipleChoiceField(choices=Degree.choices)
    category = serializers.ChoiceField(choices=Project.Category.choices)
    project_type = serializers.MultipleChoiceField(
        choices=Project.ProjectType.choices)
    duration = serializers.ChoiceField(choices=Project.Duration.choices)

    class Meta:
        model = Project
        fields = ['id', 'prof', 'title', 'description', 'cpi', 'vacancy', 'min_year', 'duration', 'learning_outcome',
                  'prereq', 'selection_procedure', 'release_date', 'last_date', 'tags', 'degree', 'project_type', 'is_paid', 'category']

    def is_valid(self, raise_exception):
        tags = self.initial_data['tags']
        self.initial_data._mutable = True
        del self.initial_data['tags']

        ret_val = super().is_valid(raise_exception=raise_exception)

        try:
            process_interests(interests_text=tags, obj=self.instance.tags)
        except:
            pass

        return ret_val

    def save(self, **kwargs):
        instance = super().save()
        if('prof' in kwargs.keys()):
            instance.prof = kwargs['prof']
        if('tags' in kwargs.keys()):
            process_interests(kwargs['tags'], self.instance.tags)
        instance.save()
        return instance


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Status.choices)

    class Meta:
        model = Application
        fields = ['id', 'student', 'project', 'preference',
                  'cover_letter', 'experience', 'status', 'remark']
