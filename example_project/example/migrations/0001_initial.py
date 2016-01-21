# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_vimeo.fields
import django_vimeo.storage


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vimeo_uri', django_vimeo.fields.VimeoField(storage=django_vimeo.storage.VimeoFileStorage(), null=True, upload_to=b'', blank=True)),
            ],
        ),
    ]
