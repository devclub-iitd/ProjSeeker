
from .models import *

from typing import Callable
from django_filters.conf import settings
from django_filters import rest_framework as filters
from django.db.models.query_utils import Q


class LazyMultipleChoiceFilter(filters.filters.MultipleChoiceFilter):
    def get_field_choices(self):
        choices = self.extra.get('choices', [])
        if isinstance(choices, Callable):
            choices = choices()
        return choices

    @property
    def field(self):
        if not hasattr(self, '_field'):
            field_kwargs = self.extra.copy()

            if settings.DISABLE_HELP_TEXT:
                field_kwargs.pop('help_text', None)

            field_kwargs.update(choices=self.get_field_choices())

            self._field = self.field_class(label=self.label, **field_kwargs)
        return self._field


class ProjectFilter(filters.FilterSet):

    search = filters.filters.CharFilter(method='search_project')
    applied = filters.filters.BooleanFilter(method='filter_applied')
    bookmarked = filters.filters.BooleanFilter(method='filter_bookmarked')
    floated = filters.filters.BooleanFilter(method='filter_floated')
    exclude_passed = filters.filters.BooleanFilter(
        method='filter_out_passed')

    status = filters.filters.ChoiceFilter(
        choices=Status.choices, method='filter_appl_status')
    is_paid = filters.filters.BooleanFilter(field_name='is_paid')

    prof__dept = filters.filters.MultipleChoiceFilter(
        choices=Departments.choices)
    degree__icontains = filters.filters.MultipleChoiceFilter(
        choices=Degree.choices)
    project_type__icontains = filters.filters.MultipleChoiceFilter(
        choices=Project.ProjectType.choices)
    duration__icontains = filters.filters.MultipleChoiceFilter(
        choices=Project.Duration.choices)
    category__icontains = filters.filters.MultipleChoiceFilter(
        choices=Project.Category.choices)
    tag = LazyMultipleChoiceFilter(
        field_name='tags__research_field', choices=Interests.to_choices)

    def search_project(self, queryset, name, value):
        q = Q(title__icontains=value)
        q |= Q(description__icontains=value)
        q |= Q(prof__user__first_name__icontains=value)
        q |= Q(prof__user__last_name__icontains=value)
        return queryset.filter(q)

    def filter_applied(self, queryset, name, value):
        user = self.request.user
        if not isStudent(user):
            return queryset.none()

        applied = Application.objects.select_related(
            'project').filter(student__user=user)
        pids = [appl.project.id for appl in applied]

        return queryset.filter(id__in=pids)

    def filter_bookmarked(self, queryset, name, value):
        user = self.request.user

        bookmarked = Bookmark.objects.filter(user=user)
        pids = [bmk.project.id for bmk in bookmarked]

        return queryset.filter(id__in=pids)

    def filter_floated(self, queryset, name, value):
        user = self.request.user
        if not isProf(user):
            return queryset.none()

        return queryset.filter(prof__user=user)

    def filter_appl_status(self, queryset, name, value):

        user = self.request.user
        appls = Application.objects.filter(
            student__user=user, status=value)
        pids = [appl.project.id for appl in appls]

        return queryset.filter(id__in=pids)

    def filter_out_passed(self, queryset, name, value):
        from datetime import datetime as dt
        return queryset.filter(last_date__gte=dt.now())

    class Meta:
        model = Project
        fields = ['title', 'prof']
