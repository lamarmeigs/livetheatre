# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20150316_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='audition',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 1, 0, 0), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='production',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 1, 0, 0), auto_now_add=True),
            preserve_default=False,
        ),
    ]
