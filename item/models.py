import uuid
import os

from user.models import User

from django.db import models
from rest_framework.exceptions import ValidationError


class Item(models.Model):
    OFFER = 'O'
    SEARCH = 'S'
    TYPES = [
        (OFFER, 'Offer'),
        (SEARCH, 'Search'),
    ]


    title = models.CharField(max_length=32)

    type = models.CharField(max_length=1, choices=TYPES, default=OFFER)
    description = models.TextField()
    itemID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    updated = models.DateTimeField(auto_now = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    reserved = models.BooleanField(default=False)


    is_active = models.BooleanField(default=True)
    flagged = models.BooleanField(default=False)
    sharecircle = models.ManyToManyField("ShareCircle")

    def __str__(self):
        return self.title

def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(str(instance.forItems.itemID), filename)

def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class ItemPictures(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    itemPicture = models.ImageField(upload_to=content_file_name,
                                    max_length=800,
                                    validators=[validate_image])
    forItems = models.ForeignKey(Item, on_delete=models.DO_NOTHING,
                                 related_name='images')


class ShareCircle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=140, blank=True, null=True)
    user = models.ManyToManyField(User)
    admin = models.ManyToManyField(User, related_name='sharecircle_admin_set')

