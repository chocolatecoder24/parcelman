from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from core.models import *
from django.utils import timezone

@csrf_exempt
@login_required(login_url="/courier/sign-in")
def available_jobs_api(request):
    jobs = list(JobListing.objects.filter(status=JobListing.PROCESSING_STATUS).values())
    
    return JsonResponse({
        "success": True,
        "jobs": jobs
    })

@csrf_exempt
@login_required(login_url="/courier/sign-in")
def current_job_update_api(request, job_id):
    job = JobListing.objects.filter(
        id=job_id,
        courier=request.user.courier,
        status__in= [
            JobListing.PICKING_STATUS,
            JobListing.DELIVERING_STATUS
        ]
    ).last()

    if job.status == JobListing.PICKING_STATUS:
        job.pickup_photo = request.FILES['pickup_photo']
        job.pickedup_at = timezone.now()
        job.status = JobListing.DELIVERING_STATUS
        job.save()

        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)("job_" + str(job.id),{
                'type': 'job_update',
                'job': {
                    'status': job.get_status_display(),
                    'pickup_photo': job.pickup_photo.url,
                }
            })
        except:
            pass

    elif job.status == JobListing.DELIVERING_STATUS:
        job.delivery_photo = request.FILES['delivery_photo']
        job.delivered_at = timezone.now()
        job.status = JobListing.COMPLETED_STATUS
        job.save()

        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)("job_" + str(job.id),{
                'type': 'job_update',
                'job': {
                    'status': job.get_status_display(),
                    'delivery_photo': job.delivery_photo.url,
                }
            })
        except:
            pass

    return JsonResponse({
        "success": True
    })

@csrf_exempt
@login_required(login_url="/courier/sign-in")
def fcm_token_update_api(request):
    request.user.courier.fcm_token = request.GET.get('fcm_token')
    request.user.courier.save()

    return JsonResponse({
        "success": True
    })
