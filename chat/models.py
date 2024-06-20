from user.models import User
import uuid
from django.db import models

# Chats
class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user2')

# Messages
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)