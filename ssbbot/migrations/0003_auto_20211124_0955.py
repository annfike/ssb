# Generated by Django 3.2.7 on 2021-11-24 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssbbot', '0002_stuff_storage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='code',
        ),
        migrations.AddField(
            model_name='stuff',
            name='code',
            field=models.ImageField(blank=True, upload_to='QR', verbose_name='картинка'),
        ),
    ]
