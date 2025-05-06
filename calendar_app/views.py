from accounts.models import Lawyer, Client
from django.shortcuts import get_object_or_404
from .forms import CalendarEventForm
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from .models import CalendarEvent

def get_logged_in_lawyer(request):
    lawyer_id = request.session['lawyer_id']
    return get_object_or_404(Lawyer, lawyer_id=lawyer_id)

def calendar_view(request):
    lawyer = get_logged_in_lawyer(request)
    events = CalendarEvent.objects.filter(created_by=lawyer)  # Correct query for events
    return render(request, 'calendar/calendar.html', {'lawyer': lawyer, 'events': events})

def create_event_view(request):
    lawyer = get_logged_in_lawyer(request)

    if request.method == 'POST':
        form = CalendarEventForm(request.POST, lawyer=lawyer)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = lawyer
            event.client = event.case.client
            event.save()
            return redirect('calendar_view')
    else:
        form = CalendarEventForm(lawyer=lawyer)
        
    return render(request, 'calendar/create_event.html', {'form': form})

def calendar_events_json(request):
    lawyer = get_logged_in_lawyer(request)
    events = CalendarEvent.objects.filter(created_by=lawyer).select_related('case__client')

    data = [{
        'id': e.event_id,  # FullCalendar uses this as the event ID
        'event_id': e.event_id,  # Used explicitly in JS for buttons
        'title': e.event_title,
        'start': e.start_time.isoformat(),
        'end': e.end_time.isoformat(),
        'description': e.event_description,
        'type': e.event_type,
        'location': e.event_loc,
        'client': e.client.client_name if e.client else '',
        'case': e.case.case_title if e.case else '',
    } for e in events]

    return JsonResponse(data, safe=False)

def edit_event_view(request, event_id):
    lawyer = get_logged_in_lawyer(request)
    event = get_object_or_404(CalendarEvent, event_id=event_id, created_by=lawyer)

    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event, lawyer=lawyer)
        if form.is_valid():
            form.save()
            return redirect('calendar_view')
    else:
        form = CalendarEventForm(instance=event, lawyer=lawyer)
    
    return render(request, 'calendar/edit_event.html', {'form': form, 'event': event})

def delete_event_view(request, event_id):
    lawyer = get_logged_in_lawyer(request)
    event = get_object_or_404(CalendarEvent, event_id=event_id, created_by=lawyer)
    event.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_logged_in_client(request):
    client_id = request.session['client_id']
    return get_object_or_404(Client, client_id=client_id)

def client_calendar_view(request):
    client = get_logged_in_client(request)
    return render(request, 'calendar/client_calendar.html', {'client': client})

def client_events_json(request):
    client = get_logged_in_client(request)
    events = CalendarEvent.objects.filter(client=client)

    data = [{
        'title': e.event_title,
        'start': e.start_time.isoformat(),
        'end': e.end_time.isoformat(),
        'description': e.event_description,
        'location': e.event_loc,
        'event_type': e.event_type,
        'lawyer': e.created_by.lawyer_name,
        'case': e.case.case_title if e.case else ''
    } for e in events]

    return JsonResponse(data, safe=False)