from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

from django.contrib import messages

from core.models import *

from core.courier import forms


# Create your views here.

@login_required
def home(request):
    return redirect(reverse('courier:available_jobs'))

@login_required(login_url="/sign-in/?next=courier")
def available_jobs_page(request):
    return render(request, 'courier/available_jobs.html', {
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY
    })
    
@login_required(login_url="/sign-in/?next=courier")
def available_job_page(request, job_id):
    job = JobListing.objects.filter(id=job_id, status=JobListing.PROCESSING_STATUS).last()
    
    if not job:
        return redirect(reverse('courier:available_jobs'))

    has_current_job =JobListing.objects.filter(
        courier = request.user.courier,
        status__in = [
            JobListing.PICKING_STATUS
        ] 
    ).exists()
    
    if has_current_job:
        messages.warning(request, "You currently have a job, finish and then accept a new one")
        return redirect(reverse('courier:current_jobs'))


    if request.method == "POST":
        job.courier = request.user.courier
        job.status = JobListing.PICKING_STATUS
        job.save()

        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)("job_" + str(job.id),{
                'type': 'job_update',
                'job': {
                    'status': job.get_status_display(),
                }
            })
        except:
            pass

        return redirect(reverse('courier:current_jobs'))

    return render(request, 'courier/available_job.html', {
        "job": job
    })

@login_required(login_url="/sign-in/?next=courier")
def current_jobs_page(request):
    job = JobListing.objects.filter(
        courier=request.user.courier, 
        status__in = [
            JobListing.PICKING_STATUS,
            JobListing.DELIVERING_STATUS
        ]
    ).last()
    
    return render(request, 'courier/current_jobs.html', {
        "job": job,
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY
    })

@login_required(login_url="/sign-in/?next=courier")
def current_job_take_page(request, job_id):
    current_job = JobListing.objects.filter(
        id=job_id,
        courier=request.user.courier,
        status__in= [
            JobListing.PICKING_STATUS,
            JobListing.DELIVERING_STATUS
        ]
    ).last()

    if not current_job:
        return redirect(reverse('courier:current_jobs'))

    return render(request, 'courier/current_job_take_photo.html', {
        "current_job": current_job
    })

@login_required(login_url="/sign-in/?next=courier")
def job_complete_page(request, job_id):
    current_job = JobListing.objects.filter(
        id=job_id,
        courier=request.user.courier,
        status__in= [
            JobListing.COMPLETED_STATUS
        ]
    ).last()

    if not current_job:
        return redirect(reverse('courier:current_jobs'))

    return render(request, 'courier/job_completed.html', {
        "current_job": current_job
    })

@login_required(login_url="/sign-in/?next=courier")
def archived_jobs_page(request):
    jobs = JobListing.objects.filter(
        courier=request.user.courier,
        status__in=[
            JobListing.COMPLETED_STATUS
        ]
    )

    earning_fee = round(sum(job.price for job in jobs ) * 0.95, 2)


    return render(request, 'courier/archived_jobs.html', {
        "jobs": jobs,
        "earning_fee": earning_fee

    })

@login_required(login_url="/sign-in/?next=courier")
def profile_page(request):
    jobs = JobListing.objects.filter(
        courier=request.user.courier,
        status__in=[
            JobListing.COMPLETED_STATUS
        ]
    )

    total_earnings = round(sum(job.price for job in jobs ) * 0.95, 2)
    total_jobs = len(jobs)
    total_km = round(sum(job.distance for job in jobs), 2)
    total_time = sum(job.duration for job in jobs)

    return render(request, 'courier/profile.html', {
        "total_earnings": total_earnings,
        "total_jobs": total_jobs,
        "total_km": total_km,
        "total_time": total_time,
        "jobs": jobs

    })

@login_required(login_url="/sign-in/?next=courier")
def courier_payment_method_page(request):
    courier_payment_form = forms.CourierPaymentForm(instance=request.user.courier)

    if request.method == 'POST':
        courier_payment_form = forms.CourierPaymentForm(request.POST, instance=request.user.courier)
        if courier_payment_form.is_valid():
            courier_payment_form.save()

            messages.success(request, "Payment Settings Updated Successfully.")
            return redirect(reverse('courier:profile'))
    return render(request, 'courier/payout_form_settings.html', {
       "courier_payment_form": courier_payment_form 
    })

@login_required(login_url="/sign-in/?next=courier")
def courier_settings_page(request):
    courier_form = forms.BasicUserForm(instance=request.user)
    courier_settings_form = forms.CourierSettingsForm(instance=request.user.courier)

    if request.method == 'POST':
        courier_form = forms.BasicUserForm(request.POST, instance=request.user)
        courier_settings_form = forms.CourierSettingsForm(request.POST, request.FILES, instance=request.user.courier)
        if courier_settings_form.is_valid() and courier_form.is_valid():
            courier_form.save()
            courier_settings_form.save()

            messages.success(request, "Courier Settings Updated Successfully.")
            return redirect(reverse('courier:courier_settings'))

    return render(request, 'courier/courier_form_settings.html', {
       "courier_settings_form": courier_settings_form,
       "courier_form": courier_form
    })