# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-30 01:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_delegate'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='delegate',
            unique_together=set([('email_user', 'organisation')]),
        ),
    ]
