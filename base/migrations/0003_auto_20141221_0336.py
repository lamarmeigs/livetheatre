# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20141221_0207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='production_company',
            field=models.ForeignKey(blank=True, to='base.ProductionCompany', help_text=b'Leave this field blank if the production is a one-person show.', null=True),
            preserve_default=True,
        ),
    ]
