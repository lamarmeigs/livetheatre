# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20150316_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='artsnews',
            name='related_company',
            field=models.ForeignKey(blank=True, to='base.ProductionCompany', on_delete=models.CASCADE, help_text=b'If appropriate, specify the production company that this story addresses.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artsnews',
            name='related_production',
            field=models.ForeignKey(blank=True, to='base.Production', on_delete=models.CASCADE, help_text=b'If appropriate, specify the production that this story addresses.', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='artsnews',
            name='content',
            field=models.TextField(help_text=b'Add the main content of the news story here. Do not include any content from other fields or related objects (such as video embeds, slideshow images, or related production or company details).', null=True, blank=True),
            preserve_default=True,
        ),
    ]
