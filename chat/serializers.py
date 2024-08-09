from rest_framework import serializers
from .models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'read', 'created_at', 'user', 'chat']
        read_only_fields = ('user', 'chat')

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude =['read', 'created_at', 'user', 'chat', 'id', 'text']
        read_only_fields = ['read', 'created_at', 'user', 'chat', 'id', 'text']

class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = '__all__'
        read_only_fields = ('user1',)