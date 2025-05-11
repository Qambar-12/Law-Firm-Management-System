from django.db import models
from cases.models import Case
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ChatRoom(models.Model):
    room_id = models.AutoField(primary_key=True)
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='chatroom')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom for Case: {self.case.case_title}"

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    sender_object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender} at {self.timestamp}"

class MessageReadTracker(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_status')
    reader_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    reader_object_id = models.PositiveIntegerField()
    reader = GenericForeignKey('reader_content_type', 'reader_object_id')
    
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message.message_id} read by {self.reader} at {self.read_at}"