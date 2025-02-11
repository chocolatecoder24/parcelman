from django import forms
from django.contrib.auth.models import User

from core.models import Customer, JobListing

class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        
        
class BasicCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('avatar',)
        
class JobCreateStep1Form(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ('name', 'description', 'category', 'size', 'quantity', 'photo')
        
class JobCreateStep2Form(forms.ModelForm):
    pickup_address = forms.CharField(required=True)
    pickup_name = forms.CharField(required=True)
    pickup_phone = forms.CharField(required=True)
    
    
    class Meta:
        model = JobListing
        fields = ('pickup_address', 'pickup_lat', 'pickup_lng', 'pickup_name', 'pickup_phone')
        
class JobCreateStep3Form(forms.ModelForm):
    delivery_address = forms.CharField(required=True)
    delivery_name = forms.CharField(required=True)
    delivery_phone = forms.CharField(required=True)
    
    
    class Meta:
        model = JobListing
        fields = ('delivery_address', 'delivery_lat', 'delivery_lng', 'delivery_name', 'delivery_phone')
        
class JobCreateStep4Form(forms.ModelForm):
    price = forms.CharField(disabled= True)
    
    class Meta:
        model = JobListing
        fields = ('price',)