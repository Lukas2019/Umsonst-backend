from turtle import title
from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from firebase_admin.messaging import Message
from fcm_django.models import FCMDevice

@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    user = instance.chat.user_1 if instance.chat.user_1 != instance.user else instance.chat.user_2
    # You can still use .filter() or any methods that return QuerySet (from the chain)
    devices = FCMDevice.objects.filter(user=user).all()
    # send_message parameters include: message, dry_run, app
    devices.send_message(Message(data={
        title: instance.user.username,
        body: instance.content,
    }))