
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
import json
from channels.generic.websocket import WebsocketConsumer

class UnreadMessagesCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}_unread_messages"

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This method can be used to handle messages received from the WebSocket
        pass

    async def send_unread_count(self, event):
        unread_count = event['unread_count']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'unread_count': unread_count
        }))

'''
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the received message to all clients
        self.send(text_data=json.dumps({
            'message': message
        }))
'''

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
        