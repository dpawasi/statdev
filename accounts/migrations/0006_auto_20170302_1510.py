# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 07:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20170302_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='abn',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='ABN'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]