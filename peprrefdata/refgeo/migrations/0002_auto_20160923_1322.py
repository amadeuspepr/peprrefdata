# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.db import models, migrations, transaction
from GeoBases import GeoBase
from django.conf import settings
from peprrefdata import get_or_none, get_or_default
from django.db.utils import IntegrityError

lg = logging.getLogger(__name__)

html = {
     'USD': '$',
     'EUR': '€', # Euro
     'CRC': '₡', # Costa Rican Colón
     'GBP': '£', # British Pound Sterling
     'ILS': '₪', # Israeli New Sheqel
     'INR': '₹', # Indian Rupee
     'JPY': '¥', # Japanese Yen
     'KRW': '₩', # South Korean Won
     'NGN': '₦', # Nigerian Naira
     'PHP': '₱', # Philippine Peso
     'PLN': 'zł', # Polish Zloty
     'PYG': '₲', # Paraguayan Guarani
     'THB': '฿', # Thai Baht
     'UAH': '₴', # Ukrainian Hryvnia
     'VND': '₫', # Vietnamese Dong
}

def create_currencies(apps, schema_editor):
    Currency = apps.get_model("refgeo", "Currency")
    geo_c = GeoBase(data='currencies', verbose=False)
    for code in geo_c:
        cdata = geo_c.get(code)

        try:
        	p = int(cdata.get('digits_number'))
        except:
        	p = 2

        Currency.objects.create(
        	code = code,
		    prec = p,
		    name = cdata.get('currency_name')[:64],
		    html = None,
		    one_dollar = 1.0,
        )  

def remove_currencies(apps, schema_editor):
    Currency = apps.get_model("refgeo", "Currency")
    Currency.objects.all().delete()


def create_countries(apps, schema_editor):
    Currency = apps.get_model("refgeo", "Currency")
    Country = apps.get_model("refgeo", "Country")
    geo_c = GeoBase(data='countries', verbose=False)
    for code in geo_c:
        cdata = geo_c.get(code)
        try:
            geoname_id = int(cdata.get("geoname_id"))
        except:
            geoname_id = None
        Country.objects.create(
            code = code,
            code3 = cdata.get("iso_alpha3"),
            name = cdata.get("name"),
            alternateNames = "",
            capitalCode = "",
            currency = get_or_none(Currency, code=cdata.get("currency_code")),
            geonameId = geoname_id,
            population = int(cdata.get("population",0)),
            continentCode = "",
        )  


def remove_countries(apps, schema_editor):
    Country = apps.get_model("refgeo", "Country")
    Country.objects.all().delete()


def create_geonames(apps, schema_editor):
    Geoname = apps.get_model("refgeo", "Geoname")


def float_or_default(str, default_value=None):
    try:
        return float(str)
    except:
        return default_value

def parse_alternate_name(s):
    splitted = s.split('|')
    tofilter = ['post', 'link', 'iata', 'icao', 'faa']
    args = [iter(splitted)] * 2
    return [(lang.lstrip('='), name) for lang, name in izip_longest(*args) \
            if name and lang.lstrip('=') not in tofilter]

def parse_alternate_name_section(section):
    tofilter = ['post', 'link', 'iata', 'icao', 'faa']
    cleaned_names = [ (lang, name) for (lang, name, _) in section if name and lang not in tofilter ]
    alternateNames = '|'.join('@'.join(couple) for couple in cleaned_names)
    if len(alternateNames) > 10000:
        return alternateNames[:alternateNames.rfind('|', 0, 10000)]
    return alternateNames

def remove_geonames(apps, schema_editor):
    Geoname = apps.get_model("refgeo", "Geoname")
    Geoname.objects.all().delete()

def create_airports(apps, schema_editor):
    Airport = apps.get_model("refgeo", "Airport")
    Country = apps.get_model("refgeo", "Country")

    PEPR_REFERENCE_GEO_AIRPORT_PAGERANK_GT = getattr(settings, "PEPR_REFERENCE_GEO_AIRPORT_PAGERANK_GT", -1)

    geo_por = GeoBase(data='ori_por',key_fields=['city_code','iata_code'], discard_dups=True)
    for code in geo_por:
        with transaction.atomic():
            cdata = geo_por.get(code)
            location_type = cdata.get("location_type")
            page_rank = float_or_default(cdata.get("page_rank"),0)
            if page_rank <= PEPR_REFERENCE_GEO_AIRPORT_PAGERANK_GT:
                continue
            try:
                Airport.objects.create(
                    iataCode = cdata.get("iata_code"),
                    icao_code = cdata.get("icao_code"),
                    location_type = location_type,
                    is_airport = ('A' in location_type),
                    all_airports = ('C' in location_type)    ,
                    #geoname = cdata.get("geoname_id")
                    name = cdata.get("name"),
                    #alternateNames = parse_alternate_name_section(cdata.get('alt_name_section')),
                    timezone = cdata.get("timezone"),
                    stateCode = cdata.get("state_code"),
                    country = get_or_none(Country, pk=cdata.get("country_code")),
                    cityCode = cdata.get("city_code"),
                    cityName = cdata.get("city_name_utf"),
                    lat = float_or_default(cdata.get("lat")),
                    lng = float_or_default(cdata.get("lng")),
                    page_rank = page_rank,
                )
            except IntegrityError as e:
                lg.error("Not unique: %s", code)


def remove_airports(apps, schema_editor):
    Airport = apps.get_model("refgeo", "Airport")
    Airport.objects.all().delete()


dependencies = {
    "Country" : "Currency",
    "Airport" : "Country",
}
tables = set(settings.PEPR_REFERENCE_GEO_LOADDATA)

while True:
    addition = False
    for item in list(tables):
        dep = dependencies.get(item)
        if dep is not None and dep not in tables:
            tables.add(dep)
            addition = True
    if not addition:
        break

operations = []
if "Currency" in tables:
    operations.append(migrations.RunPython(create_currencies, remove_currencies))

if "Country" in tables:
    operations.append(migrations.RunPython(create_countries, remove_countries))

if "Geoname" in tables:
    operations.append(migrations.RunPython(create_geonames, remove_geonames))

if "Airport" in tables:
    operations.append(migrations.RunPython(create_airports, remove_airports))

class Migration(migrations.Migration):

    dependencies = [
        ('refgeo', '0001_initial'),
    ]

    operations = operations
