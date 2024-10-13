from email import message
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q

@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    if created:
        resiving_user = instance.chat.user1 if instance.user == instance.chat.user2 else instance.chat.user2
        unread_count = Message.objects.filter(chat=instance.chat, read=False).exclude(user=resiving_user).count()
        unread_general_count = Message.objects.filter(
            Q(chat__user1=instance.user) | Q(chat__user2=instance.user),
            read=False
        ).exclude(user=resiving_user).count()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{resiving_user.id}_unread_messages",
            {
                'type': 'send_unread_count',
                'unread_count': unread_count,
                'chat_id': str(instance.chat.id)
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{resiving_user.id}_general_unread_messages",
            {
                'type': 'send_general_unread_count',
                'unread_count': unread_general_count,
            }
        )
        print("Message created:", instance.chat.id,":")
        async_to_sync(channel_layer.group_send)(
            f"{instance.chat.id}",
            {
                'type': 'send_message',
                'message': instance.text,
                'user_id': str(instance.user.id),
            }
        )