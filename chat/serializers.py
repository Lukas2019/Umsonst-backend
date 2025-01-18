from rest_framework import serializers

from item.models import Item
from .models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'read', 'created_at', 'user', 'chat', 'type']
        read_only_fields = ('user', 'chat')

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude =['read', 'created_at', 'user', 'chat', 'id', 'text']
        read_only_fields = ['read', 'created_at', 'user', 'chat', 'id', 'text']

class ChatSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), required=True)

    class Meta:
        model = Chat
        fields = "__all__"
        read_only_fields = ('user1',)