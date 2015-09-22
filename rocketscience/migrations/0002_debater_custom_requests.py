# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rocketscience', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='debater',
            name='custom_requests',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
