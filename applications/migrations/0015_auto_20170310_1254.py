# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-10 04:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0014_referral_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Submitted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='application',
            name='state',
            field=models.IntegerField(choices=[(1, 'Draft'), (2, 'With admin'), (3, 'With referee'), (4, 'With assessor'), (5, 'With manager'), (6, 'Issued'), (7, 'Issued (with admin)'), (8, 'Declined'), (9, 'New')], default=1, editable=False),
        ),
    ]
