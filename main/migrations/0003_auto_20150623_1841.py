# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150623_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(unique=True, max_length=True),
        ),
    ]
