from django import forms
from .models import MenstrualCycle

class MenstrualCycleForm(forms.ModelForm):
    class Meta:
        model = MenstrualCycle
        fields = ['last_period', 'cycle_length', 'period_duration', 'cycle_regular','age',
            'height',
            'weight']
