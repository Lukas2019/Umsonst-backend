from django.urls import re_path
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/unread_messages_count/$', consumers.UnreadMessagesCountConsumer.as_asgi()),
    path('ws/chat/', consumers.ChatConsumer),
]
