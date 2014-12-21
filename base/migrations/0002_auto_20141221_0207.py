# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'addresses'},
        ),
        migrations.AlterModelOptions(
            name='artsnews',
            options={'verbose_name_plural': 'arts news items'},
        ),
        migrations.AlterModelOptions(
            name='productioncompany',
            options={'verbose_name_plural': 'production companies'},
        ),
        migrations.AlterField(
            model_name='audition',
            name='poster',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audition',
            name='title',
            field=models.CharField(help_text=b"If none, defaults to 'Audition for *play*, by *company*'", max_length=150, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='production',
            name='poster',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='review',
            name='cover_image',
            field=filebrowser.fields.FileBrowseField(help_text=b'Image to display at the top of the review and in the homepage feature area', max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.CharField(help_text=b"If blank, defaults to 'Review: *production*'", max_length=150, null=True, blank=True),
            preserve_default=True,
        ),
    ]
