# Generated by Django 4.2.3 on 2023-07-23 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0008_gamesessionevent_serves_missed'),
    ]

    operations = [
        migrations.AddField(
            model_name='systeminfo',
            name='operating_system',
            field=models.CharField(default='Windows', max_length=50),
            preserve_default=False,
        ),
    ]