# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-02 06:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_auto_20170530_1659'),
        ('approvals', '0002_auto_20170601_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='applications.Application'),
        ),
    ]
