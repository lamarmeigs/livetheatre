# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20141231_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionPoster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filebrowser.fields.FileBrowseField(max_length=200)),
                ('order', models.IntegerField(default=0, help_text=b'Optional: set the order in which this image should be displayed.')),
                ('production', models.ForeignKey(to='base.Production', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['production', 'order'],
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='SlideshowImage',
            new_name='NewsSlideshowImage',
        ),
        migrations.AlterField(
            model_name='production',
            name='poster',
            field=filebrowser.fields.FileBrowseField(help_text=b'If this production has multiple posters, place the most relevant here. Add the others to the secondary posters formset.', max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
