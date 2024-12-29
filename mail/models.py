from django.utils import timezone

from django.db import models
from django.template.loader import render_to_string
from rest_framework.templatetags.rest_framework import render_field

from um_be.email_utils import send_html_mail
from user.models import User


class BulkEmail(models.Model):
    subject = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        # Send email
        for user in User.objects.all():
            email_html = render_to_string('email/bulk_email.html',
                                          {'text': self.text,
                                                    'user': user.username})
            send_html_mail(self.subject, email_html, [user.email])
        self.sent = True
        self.sent_at = timezone.now()
        super().save(*args, **kwargs)
