# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20141224_0036'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideshowImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filebrowser.fields.FileBrowseField(max_length=200)),
                ('order', models.IntegerField(default=0, help_text=b'Optional: set the order in which this image should be displayed.')),
                ('news', models.ForeignKey(to='base.ArtsNews')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='artsnews',
            name='video_embed',
            field=models.CharField(help_text=b'If this story includes a video, enter the embed code here to feature it on the homepage.', max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='externalreview',
            name='source_name',
            field=models.CharField(help_text=b'Provide the name of the reviewer or the group that published it.', max_length=100),
            preserve_default=True,
        ),
    ]
