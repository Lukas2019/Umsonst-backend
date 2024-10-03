from django.contrib import admin

from .models import Item, ItemPictures, ShareCircle

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'itemID', 'type')


class ShareCircleAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemPictures)
admin.site.register(ShareCircle, ShareCircleAdmin)