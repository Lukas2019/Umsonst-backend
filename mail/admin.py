from django.contrib import admin

from .models import BulkEmail

class MailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at')
    
# Register your models here.
admin.site.register(BulkEmail, MailAdmin)