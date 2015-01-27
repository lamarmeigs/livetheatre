# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20150108_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncompany',
            name='logo',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
