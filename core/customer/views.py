import requests

import firebase_admin
from firebase_admin import credentials, auth, messaging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from core.customer import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.conf import settings

from core.models import *

cred = credentials.Certificate(settings.FIREBASE_ADMIN_CREDENTIAL)
firebase_admin.initialize_app(cred)

# Create your views here.

@login_required
def home(request):
    return redirect(reverse('customer:profile'))

@login_required(login_url="/sign-in/?next=/customer/")
def profile_page(request):
    customer_form = forms.BasicUserForm(instance=request.user)
    customer_profile_form = forms.BasicCustomerForm(instance=request.user.customer)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == "POST":
        
        if request.POST.get('action') == 'update_profile':
            customer_form = forms.BasicUserForm(request.POST, instance=request.user)
            customer_profile_form = forms.BasicCustomerForm(request.POST, request.FILES, instance=request.user.customer)
            
            if customer_form.is_valid() and customer_profile_form.is_valid():            
                customer_form.save()
                customer_profile_form.save()
                
                messages.success(request, 'Your profile has been updated')
                return redirect(reverse('customer:profile'))
        
        elif request.POST.get('action') == 'update_password':    
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Your password has been updated')
                return redirect(reverse('customer:profile'))
        elif request.POST.get('action') == 'update_phone':
            #Get Firebase user data
            firebase_user = auth.verify_id_token(request.POST.get('id_token'))
            
            request.user.customer.phone_number = firebase_user['phone_number']
            request.user.customer.save()
            
            return redirect(reverse('customer:profile'))
            
            
    return render(request, 'customer/profile.html', {
        "customer_form": customer_form,
        "customer_profile_form": customer_profile_form,
        "password_form": password_form
    })
    
@login_required(login_url="/sign-in/?next=/customer/")
def create_job_page(request):
    current_customer = request.user.customer
    
    has_current_job =JobListing.objects.filter(
        customer = current_customer,
        status__in = [
            JobListing.PROCESSING_STATUS,
            JobListing.PICKING_STATUS,
            JobListing.DELIVERING_STATUS,
        ]   
    ).exists()
    
    if has_current_job:
        messages.warning(request, "You currently have a live or processing job, finish and create another one")
        return redirect(reverse('customer:current_jobs'))
        
    
    
    creating_job = JobListing.objects.filter(customer=current_customer, status=JobListing.CREATING_STATUS).last()
    step1_form = forms.JobCreateStep1Form(instance=creating_job)
    step2_form = forms.JobCreateStep2Form(instance=creating_job)
    step3_form = forms.JobCreateStep3Form(instance=creating_job)
    step4_form = forms.JobCreateStep4Form(instance=creating_job)
    
    
    
    if request.method == "POST":
        if request.POST.get('step') == '1':
            step1_form = forms.JobCreateStep1Form(request.POST, request.FILES, instance=creating_job)
            if step1_form.is_valid():
                creating_job = step1_form.save(commit=False)
                creating_job.customer = current_customer
                creating_job.save()
                
                return redirect(reverse('customer:create_job'))
        elif request.POST.get('step') == '2':
            step2_form = forms.JobCreateStep2Form(request.POST, instance=creating_job)
            if step2_form.is_valid():
                creating_job = step2_form.save()
                
                return redirect(reverse('customer:create_job'))
            
        elif request.POST.get('step') == '3':
            step3_form = forms.JobCreateStep3Form(request.POST, instance=creating_job)
            if step3_form.is_valid():
                creating_job = step3_form.save()
                
                try:
                    r = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&key={}".format(
                        creating_job.pickup_address,
                        creating_job.delivery_address,
                        settings.GOOGLE_MAP_API_KEY,
                    ))
                    
                    print(r.json()['rows'])
                    
                    distance = r.json()['rows'][0]['elements'][0]['distance']['value']
                    duration = r.json()['rows'][0]['elements'][0]['duration']['value']
                    creating_job.distance = round(distance / 1000, 2)
                    creating_job.duration = int(duration / 60)
                    creating_job.price = creating_job.distance * 50 #100 naira per km
                    creating_job.save()
                                        
                except Exception as e:
                    print(e)
                    messages.error(request, "unfortunately, we do not support shipping at this distance")
                    
                
                return redirect(reverse('customer:create_job'))
            
        elif request.POST.get('step') == '4':
            step4_form = forms.JobCreateStep4Form(request.POST, instance=creating_job)
            if step4_form.is_valid():
                creating_job = step4_form.save(commit=False)
                
                creating_job.status = JobListing.PROCESSING_STATUS
                creating_job.save()

                #send push nitification to all courier
                couriers = Courier.objects.all()
                registration_tokens = [i.fcm_token for i in couriers if i.fcm_token]

                message = messaging.MulticastMessage(
                    notification = messaging.Notification(
                        title = creating_job.name,
                        body = creating_job.description,
                    ),
                    webpush = messaging.WebpushConfig(
                        notification = messaging.WebpushNotification(
                            icon = creating_job.photo.url,
                        ),
                        fcm_options = messaging.WebpushFCMOptions(
                            link = settings.NOTIFICATION_URL + reverse('courier:available_jobs'),
                        ),
                    ),
                    tokens = registration_tokens
                )
                response = messaging.send_multicast(message)
                print('{0} messages were sent succesfully'.format(response.success_count))


                messages.success(request,   "Listing Uploaded Successfully")
                
                return redirect(reverse('customer:home'))
            
            

                
    
    #determine the current step
    if not creating_job:
        current_step = 1
    elif creating_job.delivery_name:
        current_step = 4
    elif creating_job.pickup_name:
        current_step = 3
    else:
        current_step = 2
        
    return render(request, 'customer/create_job.html', {
        "step1_form": step1_form,
        "job": creating_job,
        "step": current_step,
        "step2_form": step2_form,
        "step3_form": step3_form,
        "step4_form": step4_form,
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
    })
    
@login_required(login_url="/sign-in/?next=/customer/")
def verify_payment_page(request, payment_ref):
    current_customer = request.user.customer
    payment = JobListing.objects.get(customer=current_customer, payment_ref=payment_ref)
    verified = payment.verify_payment()
    
    if verified:
        messages.success(request, "Payment Verification Successfull")
    else:
        messages.error(request, "Payment Verifiction Failed")
    
    return redirect(reverse('customer:create_job'))

@login_required(login_url="/sign-in/?next=/customer/")
def current_jobs_page(request):
    jobs = JobListing.objects.filter(
        customer=request.user.customer,
        status__in=[
            JobListing.PROCESSING_STATUS,
            JobListing.PICKING_STATUS,
            JobListing.DELIVERING_STATUS
        ]
    )
    return render(request, 'customer/jobs.html', {
        "jobs": jobs
    })
    
    
@login_required(login_url="/sign-in/?next=/customer/")
def archived_jobs_page(request):
    jobs = JobListing.objects.filter(
        customer=request.user.customer,
        status__in=[
            JobListing.COMPLETED_STATUS,
            JobListing.CANCELED_STATUS
        ]
    )
    return render(request, 'customer/jobs.html', {
        "jobs": jobs
    })
    
@login_required(login_url="/sign-in/?next=/customer/")
def job_page(request, job_id):
    job = JobListing.objects.get(id=job_id)
    
    if request.method =="POST" and job.status == JobListing.PROCESSING_STATUS:
        job.status =JobListing.CANCELED_STATUS
        job.save()
        
        return redirect(reverse('customer:archived_jobs'))
    
    return render(request, 'customer/job.html', {
        "job": job,
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY
    })

    