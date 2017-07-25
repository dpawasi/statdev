# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-13 08:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0018_auto_20170712_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='apply_on_behalf_of',
            field=models.IntegerField(blank=True, choices=[(1, 'On Behalf of yourself'), (2, 'On Behalf of your company'), (3, 'On Behalf of indivdual as somebody else (as an authorised agent)'), (4, 'On Behalf of a company as somebody else (as an authorised agent)')], null=True),
        ),
    ]