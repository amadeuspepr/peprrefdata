import re
from peprrefdata.refgeo.models import Country, Airport
from peprrefdata import get_or_none, asciiname
from peprrefdata.autocomplete.ambiguous import disambiguate
from peprrefdata import alternate_names_list, getCityOrAirportCountryName
from peprrefdata import VALID_LANGUAGES, PSEUDO_LANG

import logging
lg = logging.getLogger(__name__)

def split_input(string, *args, **kwargs):
    return re.split("\W+", string.lower())

def city_name(city, ccache):
    name = city.name
    if city.stateCode:
        state = get_or_none(State, country=city.country, stateCode=city.stateCode)
        if state and state.name:
            name += ", "+state.name
    return "%s, %s" % (name, getCityOrAirportCountryName(city,ccache))



def make_airport_obj(cache, x, **kwargs):
    ambiguous = kwargs.get('ambiguous', [])
    try:
        _city_name = City.objects.get(cityCode=x.cityCode).name
    except:
        _city_name = x.name

    if x.all_airports and not x.is_airport:
      semantic_name = "%s (all airports)" % (_city_name)
    else:
      semantic_name = "%s (%s)" % (_city_name, x.iataCode)

    country_name = getCityOrAirportCountryName(x, cache)
    city_country = "%s, %s" % (_city_name, country_name)

    if x.name.find(_city_name) != 0:
      # airport name doesn't start with  doesn't
      airport_name = "%s - %s" % (_city_name, x.name)
    else:
      airport_name = x.name

    if ambiguous and airport_name in ambiguous:
        airport_name = "%s, %s" % (airport_name, country_name)

    return {
      "pk": x.iataCode,
      # "name": airport_name,
      # "city": city_country,
      # "alt": x.cityCode,
      # "lat": x.lat,
      # "lng": x.lng,
      # "tz":x.timezone,
      "semantic": semantic_name,
      "order": x.page_rank 
    }

def make_activity_obj(activity, **kwargs):
    return { "pk": activity.name,
             "name": activity.name}

def make_country_obj(x, **kwargs):
    capital = ''
    if x.capitalCode:
        capital = get_or_none(City, pk=x.capitalCode)
    return { 
        "pk":x.code,
        # "alt":  "|".join(alternate_names_list(x, langs=[PSEUDO_LANG])),
        # "name": x.name,
        # "lat": capital.lat if capital else None,
        # "lng": capital.lng if capital else None,
        "population": x.population
    }


def make_city_obj(cache, city, **kwargs):
    ambiguous = kwargs.get('ambiguous', [])
    include_country = kwargs.get('include_country', False)
    name = city.name
    is_main_for_name = 0
    if ambiguous and name in ambiguous:
        is_main_for_name = 1 if (ambiguous[name]==city.cityCode) else 0
        name = city_name(city, cache)
    if include_country:
        name = "%s, %s" % (name, getCityOrAirportCountryName(city, cache))
    return { "pk": city.geonameId,
             # "name": name,
             # "tz":city.timezone,
             # "lat":city.lat,
             # "lng":city.lng,
             "semantic": "%s" % city.name,
             "order": city.page_rank, #city.population,
             "main" : is_main_for_name,
            }

def make_geoname_obj(cache, geoname, **kwargs):
    ambiguous = kwargs.get('ambiguous', [])
    geoname_name = geoname.name
    country_name = geoname.country.name if geoname.country else ""
    if ambiguous and geoname_name in ambiguous:
        geoname_name = "%s, %s" % (geoname_name, country_name)

    return { "pk"   : geoname.geonameId,
             # "name" : geoname_name,
             # "tz"   : geoname.timezone,
             # "lat"  : geoname.lat,
             # "lng"  : geoname.lng,
             "order": geoname.population,
            }

def city_get_keys(city, **kwargs):
    ambiguous = kwargs.get('ambiguous', [])
    lgfilter = kwargs.get('lgfilter', False)
    #ret = set([city.cityCode, city.name, asciiname(city.name)]) \
    #          | alternate_names_list(city, lgfilter=lgfilter)\
    #          | disambiguate(city, ambiguous=ambiguous)
    ret = set([city.name, asciiname(city.name)]) \
              | alternate_names_list(city, lgfilter=lgfilter)\
              | disambiguate(city, ambiguous=ambiguous)
    return [x.lower() for x in ret]

def airport_get_keys(airport, **kwargs):
    ambiguous = kwargs.get('ambiguous', [])
    lgfilter = kwargs.get('lgfilter', False)
    ret = set([airport.iataCode, airport.name, airport.cityCode, asciiname(airport.name)]) \
              | alternate_names_list(airport, lgfilter=lgfilter) \
              | disambiguate(airport, ambiguous=ambiguous)
    return [x.lower() for x in ret]

def country_get_keys(country, **kwargs):
    lgfilter = kwargs.get('lgfilter', False)
    ret = set([country.code, country.code3, country.name])\
              | alternate_names_list(country, lgfilter=lgfilter)
    #ret = set([country.name])\
    #          | alternate_names_list(country, lgfilter=lgfilter)
    return [x.lower() for x in ret if x is not None]

def activity_get_keys(activity, **kwargs):
    activity_name = activity.name.lower()
    stemmers = kwargs.get("stemmers")
    if stemmers:
        stem = set(stemmers.get("en").stemWords(split_input(activity_name)))
        allnames = [couple.split('@') for couple in activity.alternateNames.split('|') if '@' in couple]
        for lang, name in allnames:
            stemmer = stemmers.get(lang)
            if stemmer:
                stem |= set(stemmer.stemWords(split_input(name)))
        return stem
    return [activity_name]


def geoname_get_keys(geoname, **kwargs):
  ret = set([ geoname.name ] + geoname.alternateNames.split("|"))
  return [x.lower() for x in ret if x is not None]
