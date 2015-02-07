# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_productioncompany_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='festival',
            name='plays',
        ),
        migrations.RemoveField(
            model_name='festival',
            name='production_companies',
        ),
        migrations.RemoveField(
            model_name='festival',
            name='productions',
        ),
        migrations.RemoveField(
            model_name='festival',
            name='venues',
        ),
        migrations.DeleteModel(
            name='Festival',
        ),
    ]
