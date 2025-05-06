from django import forms
from .models import CalendarEvent
from cases.models import Case
from accounts.models import Client

class CalendarEventForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = CalendarEvent
        fields = [
            'case',
            'event_title',
            'event_description',
            'start_time',
            'end_time',
            'event_type',
            'event_loc'
        ]

    def __init__(self, *args, **kwargs):
        lawyer = kwargs.pop('lawyer', None)
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if lawyer:
            # Filter cases assigned to the lawyer
            self.fields['case'].label_from_instance = lambda obj: f"{obj.case_title} ({obj.client.client_name})"


