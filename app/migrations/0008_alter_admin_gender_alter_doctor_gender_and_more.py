# Generated by Django 4.2.6 on 2023-10-16 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_account_refresh_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='gender',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='gender',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
