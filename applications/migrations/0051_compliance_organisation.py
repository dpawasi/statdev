# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-26 16:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20170602_1200'),
        ('applications', '0050_compliance_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliance',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Organisation'),
        ),
    ]
