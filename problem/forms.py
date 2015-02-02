from django import forms
from problem.models import Problem

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = [
            'name',
            'visible',
            'judge_type',
            'judge_source',
            'other_judge_id',
        ]

