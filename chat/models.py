from typing import Iterable
from user.models import User
import uuid
from django.db import models
import time

# Chats
class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user2')

# Messages
class Message(models.Model):

    TEXT = 'text'
    LOCATION = 'location'
    ITEM = 'item'
    TYPES = [
        (TEXT, 'Text'),
        (LOCATION, 'Location'),
        (ITEM, 'Item'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    type = models.CharField(max_length=100, default=TEXT, choices=TYPES)

    def save(self, *args, **kwargs):
        if not self.pk:  # Prüft, ob das Objekt neu ist
            self.created_at_unix = time.time()
        super().save(*args, **kwargs)
