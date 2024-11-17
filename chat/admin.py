from calendar import c
from django.contrib import admin
from pyparsing import C
from .models import Chat, Message

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id','user1', 'user2')

# Register your models here.
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message)