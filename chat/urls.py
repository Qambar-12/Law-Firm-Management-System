from django.urls import path
from . import views
urlpatterns = [
    path('chat_view/<int:case_id>/', views.chat_view, name='chat_view'),
    path('send-message/', views.send_message, name='send_message'),
    path('typing-event/', views.typing_event, name='typing_event'),
    path('mark_messages_as_read/', views.mark_messages_as_read, name='mark_messages_as_read'),
]