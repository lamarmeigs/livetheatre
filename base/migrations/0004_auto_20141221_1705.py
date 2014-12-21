# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0003_auto_20141221_0336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviewer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('headshot', filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True)),
                ('bio', models.TextField(null=True, blank=True)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(default=0, to='base.Reviewer'),
            preserve_default=False,
        ),
    ]
