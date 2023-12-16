from django import forms
from client_app.models import *


class OrderModelForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pharmacy', 'address']


class OrderCommentModelForm(forms.ModelForm):
    class Meta:
        model = OrderComment
        fields = ('body',)
