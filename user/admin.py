from django.contrib import admin
from .models import User, Complaint
# Register your models here.
admin.site.register(User)

admin.site.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'text')