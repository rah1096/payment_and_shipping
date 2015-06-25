# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_id', models.CharField(unique=True, max_length=255)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField()),
                ('manufacturer', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
            ],
        ),
    ]
