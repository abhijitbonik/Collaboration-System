# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-07 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Media', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='medialink',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
