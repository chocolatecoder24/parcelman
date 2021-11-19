import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import secrets
from .paystack import PayStack


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='customer/avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.get_full_name()

class Courier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='courier/avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    Account_Bank_name = models.CharField(max_length=255,blank=True)
    Account_name = models.CharField(max_length=255,blank=True)
    Account_number = models.CharField(max_length=255,blank=True)
    fcm_token = models.TextField(blank=True)
    

    def __str__(self):
        return self.user.get_full_name()

class Category(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class JobListing(models.Model):
    SMALL_SIZE = "small"
    MEDIUM_SIZE = "medium"
    LARGE_SIZE = "large"
    SIZES = (
        (SMALL_SIZE, 'Small'),
        (MEDIUM_SIZE, 'Medium'),
        (LARGE_SIZE, 'Large'),
    )
    
    CREATING_STATUS = 'creating'
    PROCESSING_STATUS = 'processing'
    PICKING_STATUS = 'picking'
    DELIVERING_STATUS = 'delivering'
    COMPLETED_STATUS = 'completed'
    CANCELED_STATUS = 'canceled'
    STATUSES = (
        (CREATING_STATUS, 'Creating'),
        (PROCESSING_STATUS, 'Processing'),
        (PICKING_STATUS, 'Picking'),
        (DELIVERING_STATUS, 'Delivering'),
        (COMPLETED_STATUS, 'completed'),
        (CANCELED_STATUS, 'Canceled'), 
    )
    
    #step 1
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=50, choices=SIZES, default=MEDIUM_SIZE)
    quantity = models.IntegerField(default=1)
    photo = models.ImageField(upload_to='jobs_listing/photos/')
    status = models.CharField(max_length=50, choices=STATUSES, default=CREATING_STATUS)
    created_at = models.DateTimeField(default=timezone.now)
    
    #step 2
    pickup_address = models.CharField(max_length=255, blank=True)
    pickup_lat = models.FloatField(default=0)
    pickup_lng = models.FloatField(default=0)
    pickup_name = models.CharField(max_length=255, blank=True)
    pickup_phone = models.CharField(max_length=50, blank=True)
    
    #step 3
    delivery_address = models.CharField(max_length=255, blank=True)
    delivery_lat = models.FloatField(default=0)
    delivery_lng = models.FloatField(default=0)
    delivery_name = models.CharField(max_length=255, blank=True)
    delivery_phone = models.CharField(max_length=50, blank=True)
    
    #step 4
    duration = models.IntegerField(default=0)
    distance = models.FloatField(default=0)
    price = models.FloatField(default=0)
    
    #step 5
    payment_ref = models.CharField(max_length=255, blank=True)
    verified_payment = models.BooleanField(default=False)
    
    #extra field
    pickup_photo = models.ImageField(upload_to='jobs_listing/pickup_photo/', null=True, blank=True)
    pickedup_at = models.DateTimeField(null=True, blank=True)
    
    delivery_photo = models.ImageField(upload_to='jobs_listing/delivery_photo/', null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    
    
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        while not self.payment_ref:
            payment_ref = secrets.token_urlsafe(50)
            object_with_similar_payment_ref = JobListing.objects.filter(payment_ref=payment_ref)
            if not object_with_similar_payment_ref:
                self.payment_ref = payment_ref
        super().save(*args, **kwargs)
        
    def amount_value(self) -> int:
        return self.price *100

    def verify_payment(self):
        paystack_pay = PayStack()
        status, result = paystack_pay.verify_payment(self.payment_ref, self.price)
        if status:
            if result['amount'] / 100 == self.price:
                self.verified_payment = True
            self.save()
            if self.verified_payment:
                return True
        return False

    
