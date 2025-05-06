from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar_view'),  # View for the calendar
    path('create/', views.create_event_view, name='create_event'),  # View for creating events
    path('events/lawyer/', views.calendar_events_json, name='calendar_events_json'),  # Endpoint for calendar events in JSON
    path('calendar/edit/<int:event_id>/', views.edit_event_view, name='edit_event'),
    path('calendar/delete/<int:event_id>/', views.delete_event_view, name='delete_event'),
    path('calendar/client', views.client_calendar_view, name='client_calendar_view'),
    path('events/clients/', views.client_events_json, name='client_events_json')
]
