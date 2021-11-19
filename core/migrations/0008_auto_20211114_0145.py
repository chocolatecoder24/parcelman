# Generated by Django 3.2.9 on 2021-11-14 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20211113_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='payment_ref',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='joblisting',
            name='verified_payment',
            field=models.BooleanField(default=False),
        ),
    ]
