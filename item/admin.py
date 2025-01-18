from django.contrib import admin

from .models import City, Item, ItemPictures, ShareCircle

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'itemID', 'type')


class ShareCircleAdmin(admin.ModelAdmin):
    list_display = ('title','id')


# admin.site.register(Item, ItemAdmin)
admin.site.register(ItemPictures)
admin.site.register(ShareCircle, ShareCircleAdmin)

class ShareCircleInline(admin.TabularInline):
    model = ShareCircle
    extra = 1

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name','id')
    inlines = [ShareCircleInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('itemID', 'title', 'flagged')
    actions = ['flag_items']

    def flag_items(self, request, queryset):
        queryset.update(flagged=True)
        self.message_user(request, "Selected items have been flagged.")
    flag_items.short_description = "Flag selected items"