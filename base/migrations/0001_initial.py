# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('line_1', models.CharField(max_length=150)),
                ('line_2', models.CharField(max_length=150, null=True, blank=True)),
                ('city', models.CharField(max_length=80)),
                ('zip_code', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtsNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150)),
                ('content', models.TextField()),
                ('external_url', models.URLField(help_text=b'If this news item links to an external location, provide the full URL.', null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(help_text=b"This field will be used in the URL for this news item's detail page.")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Audition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b"If none, defaults to 'Audition for <play>, by <company>'", max_length=150, null=True, blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(help_text=b'Leave blank if the auditions last a single day', null=True, blank=True)),
                ('event_details', models.TextField(help_text=b'Use this field to provide additional event information, such as where the event occurs, at what time, or any relevant contact information.', null=True, blank=True)),
                ('content', models.TextField(help_text=b'Use this field to provide information not directly relevant to the event, such as available roles, required experience or additional information about the production.', null=True, blank=True)),
                ('poster', models.ImageField(null=True, upload_to=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Festival',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'Yearly festivals should be distinguished by number or year', max_length=80, verbose_name=b'Festival Name')),
                ('description', models.TextField(null=True, blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(help_text=b'Leave blank for one-day festivals.', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150)),
                ('playwright', models.CharField(max_length=80, null=True, blank=True)),
                ('synopsis', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Production',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name=b'Date of first performance')),
                ('end_date', models.DateField(help_text=b'Leave blank for productions with a single performance.', null=True, verbose_name=b'Date of last performance', blank=True)),
                ('event_details', models.TextField(help_text=b'Provide additional event information, such as a weekly schedule, ticket prices, or venue details.', null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('poster', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('slug', models.SlugField(help_text=b"This field will be used in the URL for this production's detail page.")),
                ('play', models.ForeignKey(to='base.Play')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductionCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(help_text=b"Provide any additional information, such as the company's history, goals, or charter.", null=True, blank=True)),
                ('contact_info', models.TextField(null=True, verbose_name=b'Contact Information', blank=True)),
                ('company_site', models.URLField(help_text=b"Enter the full URL to the company's website.", null=True, verbose_name=b'Company Website', blank=True)),
                ('slug', models.SlugField(help_text=b"This field will be used in the URL for this company's detail page.")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b"If blank, defaults to 'Review: <production>'", max_length=150, null=True, blank=True)),
                ('cover_image', models.ImageField(help_text=b'Image to display at the top of the review and in the homepage feature area', null=True, upload_to=b'', blank=True)),
                ('content', models.TextField()),
                ('lede', models.CharField(help_text=b'Enter a brief (< 300 character) introduction to the review. If blank, the first 50 words of the content will be used on the homepage.', max_length=300, null=True, blank=True)),
                ('is_published', models.BooleanField(default=False, help_text=b'If false, this review will not be visible on the site', verbose_name=b'Published')),
                ('published_on', models.DateTimeField(help_text=b'Stores the time when this review was published.', null=True, blank=True)),
                ('slug', models.SlugField(help_text=b"This field will be used in the URL for this review's page.")),
                ('production', models.ForeignKey(to='base.Production')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('map_url', models.URLField(null=True, blank=True)),
                ('slug', models.SlugField(help_text=b"This field will be used in the URL for this venue's detail page.")),
                ('address', models.OneToOneField(to='base.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='productioncompany',
            name='home_venue',
            field=models.ManyToManyField(help_text=b'List any venues at which this company regularly performs.', to='base.Venue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='production_company',
            field=models.ForeignKey(to='base.ProductionCompany'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='venue',
            field=models.ForeignKey(to='base.Venue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='festival',
            name='plays',
            field=models.ManyToManyField(help_text=b'List plays for which no addition production information is available.', to='base.Play', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='festival',
            name='production_companies',
            field=models.ManyToManyField(help_text=b'List involved companies whose productions are unknown.', to='base.ProductionCompany', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='festival',
            name='productions',
            field=models.ManyToManyField(help_text=b'For any productions listed here, do not include the corresponding companies, plays, or venues in subsequent fields.', to='base.Production', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='festival',
            name='venues',
            field=models.ManyToManyField(help_text=b'List any involved venues whose performances are unknown.', to='base.Venue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audition',
            name='play',
            field=models.ForeignKey(blank=True, to='base.Play', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audition',
            name='production_company',
            field=models.ForeignKey(blank=True, to='base.ProductionCompany', help_text=b'The production company conducting the audition.', null=True),
            preserve_default=True,
        ),
    ]
