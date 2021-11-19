from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string, get_template


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        # send the welcome email


        # body = render_to_string(
        #     'welcome_email_template.html',
        #     {
        #         'name': instance.get_full_name(),
        #         'title': 'Welcome to Parcelman',
        #         'msg' : 'We the team at parcelman is excited to have you join us!',
        #         'img' : 'https://i.ibb.co/FxXP3T1/Png-Item-1451032.png',
        #         'ftext': 'Founders of Parcelman',
        #         'boss': 'Ikechukwu Otuya and Princewill Uzodimma'
        #     }
        # )
        # send_mail(
        #     'Welcome to Parcelman',
        #     body,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [instance.email],
        #     fail_silently=False,
        # )


        # send the welcome email

        email = { 
            'name': instance.get_full_name(),
            'title': 'Welcome to Parcelman',
            'msg' : 'We the team at parcelman is excited to have you join us!',
            'img' : 'https://i.ibb.co/FxXP3T1/Png-Item-1451032.png',
            'ftext': 'Founders of Parcelman',
            'boss': 'Ikechukwu Otuya and Princewill Uzodimma'
        }


        text_content = """
        Hello {},

        <p>We the team at parcelman is excited to have you join us!</p>
        
        <p>{}</p>
        <p>{}</p>

        p>Thank you for being part of Parcelman, a subsidiary of boleum energy and technology limited.</p>

        """.format(email['name'], email['ftext'], email['boss'])

        subject = "Welcome to Parcelman"

        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email

        html_c = get_template('welcome_email_template.html')
        context = {'email': email}
        html_content = html_c.render(context)

        message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        message.attach_alternative(html_content, 'text/html')
        message.send(fail_silently=False)
