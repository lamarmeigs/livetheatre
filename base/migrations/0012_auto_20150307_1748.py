# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20150207_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='production',
            name='on_friday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Friday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_monday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Monday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_saturday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Saturday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_sunday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Sunday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_thursday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Thursday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_tuesday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Tuesday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='on_wednesday',
            field=models.BooleanField(default=False, verbose_name=b'Occurs on Wednesday'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='production',
            name='end_date',
            field=models.DateField(help_text=b'Leave blank for events that last only a single day.', null=True, verbose_name=b'Date of last event.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='production',
            name='start_date',
            field=models.DateField(verbose_name=b'Date of first event.'),
            preserve_default=True,
        ),
    ]
