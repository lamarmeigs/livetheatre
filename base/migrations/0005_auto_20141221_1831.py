# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20141221_1705'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['line_1'], 'verbose_name_plural': 'addresses'},
        ),
        migrations.AlterModelOptions(
            name='artsnews',
            options={'ordering': ['-created_on'], 'verbose_name_plural': 'arts news items'},
        ),
        migrations.AlterModelOptions(
            name='play',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='productioncompany',
            options={'ordering': ['name'], 'verbose_name_plural': 'production companies'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['published_on']},
        ),
        migrations.AlterModelOptions(
            name='venue',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='artsnews',
            name='content',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
