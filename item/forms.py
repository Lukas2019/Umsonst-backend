from django import forms
from django.forms import ModelForm
from item.models import ItemPictures


class UploadFileForm(forms.Form):
    model = ItemPictures
    fields = ['itemPicture', 'fields']
