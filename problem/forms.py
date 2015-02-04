from django import forms
from problem.models import Problem

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = [
            'pname',
            'owner',
            'visible',
            'judge_source',
            'other_judge_id',
        ]
        labels = {
            'pname': 'Problem Name'
        }
