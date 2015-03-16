# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20150307_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='artsnews',
            name='is_job_opportunity',
            field=models.BooleanField(default=False, help_text=b'Check if this news item is about a job opportunity.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='production',
            name='event_details',
            field=models.TextField(help_text=b'Provide additional event information, such as ticket prices or daily schedules. Do not include the venue, opening/closing dates, or company information.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
