# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-29 06:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0052_auto_20180129_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliance',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='compliance_submitted_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
