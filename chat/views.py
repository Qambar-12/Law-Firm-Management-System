from django.shortcuts import get_object_or_404, render
from .models import ChatRoom, Message , MessageReadTracker
from chat.utils import pusher_client ,pusher
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from accounts.models import Lawyer, Client
from django.views.decorators.csrf import csrf_exempt

def chat_view(request, case_id):
    chatroom=ChatRoom.objects.get(case=case_id)
    chat_messages = Message.objects.filter(chatroom=chatroom).order_by('timestamp')
    case = chatroom.case
    lawyers = case.lawyers.all()
    client = case.client
    if request.session.get('lawyer_logged_in'):
        sender = get_object_or_404(Lawyer, pk=request.session.get('lawyer_id'))
    elif request.session.get('client_logged_in'):
        sender = get_object_or_404(Client, pk=request.session.get('client_id'))
    participants = list(lawyers) + [client]
    sender_type = ContentType.objects.get_for_model(sender)
    # Get message IDs this user has read
    read_ids = MessageReadTracker.objects.filter(
        reader_content_type=sender_type,
        reader_object_id=sender.pk
    ).values_list('message_id', flat=True)

     # Find first unread message index
    unread_separator_index = None
    for idx, msg in enumerate(chat_messages):
        if msg.pk not in read_ids:
            unread_separator_index = idx
            break

    return render(request, 'chat/chatroom.html', {'chatroom': chatroom, 'chat_messages': chat_messages,'participants': participants ,'sender': str(sender),'unread_separator_index': unread_separator_index})


def send_message(request):
    if request.method == "POST":
        content = request.POST.get('message')
        room_id = request.POST.get('room_id')

        chatroom = ChatRoom.objects.get(pk=room_id)
        if request.session.get('lawyer_logged_in'):
            sender = get_object_or_404(Lawyer, pk=request.session.get('lawyer_id'))
            sender_id = sender.lawyer_id
        elif request.session.get('client_logged_in'):
            sender = get_object_or_404(Client, pk=request.session.get('client_id'))
            sender_id = sender.client_id

        sender_type = ContentType.objects.get_for_model(sender)
        message = Message.objects.create(
            chatroom=chatroom,
            sender_content_type=sender_type,
            sender_object_id=sender_id,
            content=content
        )

    # Automatically mark the message as read by the sender
        MessageReadTracker.objects.create(
            message=message,
            reader_content_type=sender_type,
            reader_object_id=sender.pk
        )
        pusher_client.trigger(
            f'chatroom-{room_id}',
            'new-message',
            {
                'sender': str(sender),
                'content': content,
                'timestamp': str(message.timestamp)
            }
        )

        return JsonResponse({'status': 'Message sent'})



@csrf_exempt
def mark_messages_as_read(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        chatroom = ChatRoom.objects.get(pk=room_id)

        if request.session.get('lawyer_logged_in'):
            sender = get_object_or_404(Lawyer, pk=request.session.get('lawyer_id'))
        elif request.session.get('client_logged_in'):
            sender = get_object_or_404(Client, pk=request.session.get('client_id'))
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        sender_type = ContentType.objects.get_for_model(sender)

        # Mark all unread messages as read
        unread_messages = Message.objects.filter(
            chatroom=chatroom
        ).exclude(
            messagereadtracker__reader_content_type=sender_type,
            messagereadtracker__reader_object_id=sender.pk
        )

        for msg in unread_messages:
            MessageReadTracker.objects.create(
                message=msg,
                reader_content_type=sender_type,
                reader_object_id=sender.pk
            )

        return JsonResponse({'status': 'Messages marked as read'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def typing_event(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        sender = request.user.get_full_name() or request.user.username

        pusher.trigger(f'chatroom-{room_id}', 'typing', {
            'sender': sender,
            'timestamp': str(now())
        })
        return JsonResponse({'status': 'typing sent'})
    return JsonResponse({'error': 'Invalid method'}, status=400)