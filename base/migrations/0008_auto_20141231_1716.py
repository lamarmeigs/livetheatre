# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20141229_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slideshowimage',
            options={'ordering': ['news', 'order']},
        ),
        migrations.AlterField(
            model_name='artsnews',
            name='content',
            field=models.TextField(help_text=b'Do not include the video embed or any images from the slideshow here.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='artsnews',
            name='video_embed',
            field=models.CharField(help_text=b'If this story includes a video, enter the embed code here to feature it on the homepage. Be sure to remove any width and height attributes.', max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
