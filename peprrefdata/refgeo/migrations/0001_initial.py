# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('iataCode', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('icao_code', models.CharField(default=None, max_length=4, null=True)),
                ('location_type', models.CharField(max_length=4, null=True, blank=True)),
                ('is_airport', models.BooleanField(default=False)),
                ('all_airports', models.BooleanField(default=False)),
                ('alternateNames', models.CharField(default=b'', max_length=10000)),
                ('timezone', models.TextField(null=True)),
                ('stateCode', models.CharField(max_length=6, db_index=True)),
                ('cityCode', models.CharField(max_length=3, db_index=True)),
                ('cityName', models.TextField()),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('page_rank', models.FloatField(default=0, max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('cityCode', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('stateCode', models.CharField(max_length=6, db_index=True)),
                ('alternateNames', models.CharField(default=b'', max_length=10000)),
                ('timezone', models.TextField(null=True)),
                ('gmt_offset', models.FloatField(null=True)),
                ('dst_offset', models.FloatField(null=True)),
                ('raw_offset', models.FloatField(null=True)),
                ('precipitations', models.TextField(null=True)),
                ('temperatures', models.TextField(null=True)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('koppen', models.CharField(max_length=3, null=True, blank=True)),
                ('population', models.IntegerField(default=0, max_length=9, db_index=True)),
                ('page_rank', models.FloatField(default=0, max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('geonameId', models.IntegerField(default=0, max_length=10, db_index=True)),
                ('en_name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('code3', models.CharField(default=None, max_length=3, null=True)),
                ('alternateNames', models.TextField(default=b'')),
                ('capitalCode', models.CharField(max_length=3)),
                ('currency', models.CharField(default=None, max_length=3, null=True)),
                ('geonameId', models.IntegerField(default=0, max_length=10, db_index=True)),
                ('population', models.IntegerField(default=0, max_length=9)),
                ('continentCode', models.CharField(default=b'', max_length=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('prec', models.IntegerField(default=2, max_length=4)),
                ('name', models.CharField(default=None, max_length=64, null=True)),
                ('html', models.CharField(default=None, max_length=8, null=True)),
                ('one_dollar', models.FloatField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Geoname',
            fields=[
                ('geonameId', models.IntegerField(max_length=11, serialize=False, primary_key=True)),
                ('alternateNames', models.TextField(default=b'')),
                ('fcode', models.CharField(max_length=6)),
                ('stateCode', models.CharField(max_length=6, null=True, db_index=True)),
                ('timezone', models.TextField(null=True)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('population', models.IntegerField(default=0, max_length=9)),
                ('country', models.ForeignKey(blank=True, to='refgeo.Country', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stateCode', models.CharField(max_length=6)),
                ('name', models.TextField()),
                ('country', models.ForeignKey(blank=True, to='refgeo.Country', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('country', 'stateCode')]),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, to='refgeo.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='geoname',
            field=models.ForeignKey(blank=True, to='refgeo.Geoname', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='airport',
            name='country',
            field=models.ForeignKey(blank=True, to='refgeo.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='airport',
            name='geoname',
            field=models.ForeignKey(blank=True, to='refgeo.Geoname', null=True),
            preserve_default=True,
        ),
    ]
