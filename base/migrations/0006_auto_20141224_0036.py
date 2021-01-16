# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20141221_1831'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('review_url', models.URLField()),
                ('source_name', models.CharField(max_length=100)),
                ('production', models.ForeignKey(to='base.Production', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-published_on']},
        ),
    ]
