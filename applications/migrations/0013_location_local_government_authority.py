# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-23 02:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0012_auto_20170620_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='local_government_authority',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
