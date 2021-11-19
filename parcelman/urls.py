
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views, consumers

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core.customer import views as customer_views
from core.courier import views as courier_views, apis as courier_apis

#customer url patterns
customer_urlpatterns = [
    path('', customer_views.home, name="home"),
    path('profile/', customer_views.profile_page, name="profile"),
    path('create-a-job/', customer_views.create_job_page, name="create_job"),
    path('create-a-job/verify-payment/<str:payment_ref>/', customer_views.verify_payment_page, name="verify_payment"),
    
    path('jobs/current/', customer_views.current_jobs_page, name="current_jobs"),
    path('jobs/archived/', customer_views.archived_jobs_page, name="archived_jobs"),
    path('jobs/<str:job_id>/', customer_views.job_page, name="job"),   
]

#courier url patterns
courier_urlpatterns = [
    path('', courier_views.home, name="home"),
    path('jobs/available/', courier_views.available_jobs_page, name="available_jobs"),
    path('jobs/available/<str:job_id>/', courier_views.available_job_page, name="available_job"),
    path('jobs/current/', courier_views.current_jobs_page, name="current_jobs"),
    path('jobs/current/<str:job_id>/take-a-photo/', courier_views.current_job_take_page, name="current_job_take_photo"),
    path('jobs/successfuly-completed-a-job/<str:job_id>/', courier_views.job_complete_page, name="job_complete"),
    path('jobs/current/archived/', courier_views.archived_jobs_page, name="archived_jobs"),
    path('profile/', courier_views.profile_page, name="profile"),
    path('profile/payout-method-settings', courier_views.courier_payment_method_page, name="courier_payment_method"),
    path('profile/courier-settings', courier_views.courier_settings_page, name="courier_settings"),    
    
    path('api/jobs/available/', courier_apis.available_jobs_api, name="available_jobs_api"),
    path('api/jobs/current/<str:job_id>/update/', courier_apis.current_job_update_api, name="current_job_update_api"),
    path('api/fcm-token/update/', courier_apis.fcm_token_update_api, name="fcm_token_update_api"),
    
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social_auths')),
    path('', views.home),

    path('sign-in/', auth_views.LoginView.as_view(template_name="sign_in.html")),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/")),
    path('sign-up/', views.sign_up),



    path('customer/', include((customer_urlpatterns, 'customer'))),
    path('courier/', include((courier_urlpatterns, 'courier'))),

    path('firebase-messaging-sw.js', (TemplateView.as_view(template_name="firebase-messaging-sw.js", content_type="application/javascript",))),
    
]

websocket_urlpatterns = [
    path('ws/jobs/<str:job_id>/', consumers.JobConsumer.as_asgi()),
]

if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    