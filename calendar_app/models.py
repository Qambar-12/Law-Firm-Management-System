from django.db import models
from accounts.models import Lawyer, Client
from cases.models import Case

class CalendarEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='calendar_events')
    event_title = models.CharField(max_length=255)
    event_description = models.TextField(blank=True)
    created_by = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, related_name='created_events')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='observed_events')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_type = models.CharField(max_length=50, default='Meeting')  # default value, changeable
    event_loc = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.event_title} ({self.start_time} - {self.end_time})"
