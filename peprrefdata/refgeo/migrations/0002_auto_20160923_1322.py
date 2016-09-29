# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from GeoBases import GeoBase

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
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
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
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Currency = apps.get_model("refgeo", "Currency")
    Currency.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('refgeo', '0001_initial'),
    ]

    operations = [
    	migrations.RunPython(create_currencies, remove_currencies)
    ]
