from rest_framework import permissions
from enum import Enum
from .models import Item
#from user.models import Users

class Variant(Enum):
    Item = 0
    ItemPicture = 1

class IsOwnerPermission(permissions.BasePermission):
    """
    Allows access only to users who created an item.
    """
    type = ''

    def __init__(self, variant: Variant, *args, **kwargs):
        self.variant = variant
        super().__init__(*args, **kwargs)

    def has_permission(self, request, view):
        if self.variant == Variant.Item:
            id_obj = view.get_object().user.id
        elif self.variant == Variant.ItemPicture:
            id_obj = view.get_object().forItems.user.id
        object = view.get_object()
        if id_obj == request.user.id:
            return bool(request.user and request.user.is_authenticated)
        else:
            return False

class IsSharCircleAdminPermission(permissions.BasePermission):
    """
    Allows access only to users who are admins of related sharecircle.
    """
    type = ''

    def __init__(self, variant: Variant, *args, **kwargs):
        self.variant = variant
        super().__init__(*args, **kwargs)

    def has_permission(self, request, view):
        if self.variant == Variant.Item:
            id_obj = view.get_object().sharecircle.admin.id
        elif self.variant == Variant.ItemPicture:
            id_obj = view.get_object().forItems.sharecircle.admin.id
        object = view.get_object()
        if id_obj == request.user.id:
            return bool(request.user and request.user.is_authenticated)
        else:
            return False