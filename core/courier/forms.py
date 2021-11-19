from django import forms
from django.contrib.auth.models import User
from core.models import Courier

class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class CourierPaymentForm(forms.ModelForm):
    class Meta:
        model = Courier
        fields = ('Account_name','Account_Bank_name', 'Account_number')

class CourierSettingsForm(forms.ModelForm):
    class Meta:
        model = Courier
        fields = ('phone_number','avatar')