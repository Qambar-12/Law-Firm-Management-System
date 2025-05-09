from django import forms
from .models import CalendarEvent
from cases.models import Case
from accounts.models import Client
from django.core.exceptions import ValidationError

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
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        case = cleaned_data.get('case')

        if not all([start, end, case]):
            return cleaned_data  

        if end <= start:
            raise ValidationError("End time must be after start time.")

        overlapping_client_events = CalendarEvent.objects.filter(
            case__client=case.client,
            start_time__lt=end,
            end_time__gt=start
        )
        if self.instance.pk:
            overlapping_client_events = overlapping_client_events.exclude(pk=self.instance.pk)

        if overlapping_client_events.exists():
            raise ValidationError("This client already has an overlapping event.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        lawyer = kwargs.pop('lawyer', None)
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if lawyer:
            # Filter cases assigned to the lawyer
            self.fields['case'].label_from_instance = lambda obj: f"{obj.case_title} ({obj.client.client_name})"


