# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('code3', models.CharField(default=None, max_length=3, null=True)),
                ('name', models.TextField()),
                ('alliance_status', models.TextField(default=None, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='airline',
            name='alliance',
            field=models.ForeignKey(default=None, to='refair.Alliance', null=True),
            preserve_default=True,
        ),
    ]
