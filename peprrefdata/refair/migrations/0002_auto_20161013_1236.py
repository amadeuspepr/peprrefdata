# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from django.db import models, migrations, transaction
from GeoBases import GeoBase
from django.conf import settings
from peprrefdata import get_or_none, get_or_default
from django.db.utils import IntegrityError

def create_airlines(apps, schema_editor):
    Airline = apps.get_model("refair", "Airline")
    Alliance = apps.get_model("refair", "Alliance")
    geo_a = GeoBase(data='airlines', verbose=False, key_fields=['2char_code'])
    for code in geo_a:
        adata = geo_a.get(code)
        try:
            with transaction.atomic():
                alliance_code = adata.get('alliance_code') or None
                if alliance_code:
                    alliance, _ = Alliance.objects.get_or_create(name=alliance_code)
                else:
                    alliance = None
                Airline.objects.create(
                    code = adata.get('2char_code'),
                    code3 = adata.get('3char_code'),
                    name = adata.get('name'),
                    alliance = alliance,
                    alliance_status = adata.get('alliance_status') or None,
                )
        except IntegrityError as e:
            ex = Airline.objects.get(code = adata.get('2char_code'))
            print >>sys.stderr, adata, ex.name, ex.code3

def remove_airlines(apps, schema_editor):
    Airline = apps.get_model("refair", "Airline")
    Alliance = apps.get_model("refair", "Alliance")
    Airline.objects.all().delete()
    Alliance.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('refair', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_airlines, remove_airlines)
    ]
