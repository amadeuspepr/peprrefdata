from peprrefdata.refgeo.models import City, Airport, Country, State, Geoname
from django.db.models import Count, F
from operator import itemgetter, attrgetter
from peprrefdata import get_or_none
from places.utils import alternate_names_list

from itertools import groupby

import logging
lg = logging.getLogger(__name__)

OLD_EUROPE = ('GB', 'FR', 'ES', 'IT', 'PT', 'DE')

def find_main_city(city_group):
    european = filter(lambda c:c.countryCode in OLD_EUROPE, city_group)
    if len(european) == 1:
        # one "old europe" city
        epop = european[0].population
        major = max(map(lambda c:c.population, city_group))
        if major/epop < 10:
            # its population may be lower than the biggest contestant, but not THAT much
            # for instance, perth in UK shouldn't appear, but Toledo or Valencia in Spain should
            return european[0].cityCode

_list_ambiguous_cities = None
def list_ambiguous_cities():
    global _list_ambiguous_cities
    if _list_ambiguous_cities:
        return _list_ambiguous_cities
    lg.warning("list ambiguous cities!")
    ret = {}
    ambiguous_english_names = map(itemgetter('name'), City.objects
        .values('name')
        .annotate(count=Count('pk'))
        .filter(count__gt=1)
    )
    ambiguous_cities = City.objects.filter(name__in=ambiguous_english_names)
    for english_name, g in groupby(ambiguous_cities, attrgetter('name')):
        city_group = list(g)
        ret[english_name] = find_main_city(city_group)
    _list_ambiguous_cities = ret
    return ret

_list_ambiguous_geonames = None
def list_ambiguous_geonames():
    global _list_ambiguous_geonames
    if _list_ambiguous_geonames:
        return _list_ambiguous_geonames
    lg.warning("list ambiguous geonames!")
    ret = {}
    # geonames with same name
    _list_ambiguous_geonames = set(map(itemgetter('name'), Geoname.objects
        .values('name')
        .annotate(count=Count('pk'))
        .filter(count__gt=1)))
    # geonames with same name as countries
    _list_ambiguous_geonames |= set(map(lambda i: i.name, Geoname.objects.filter(
        name__in=Country.objects.all().values('name'))
        .exclude(country__name=F('name'))))
    return list(_list_ambiguous_geonames)


_list_ambiguous_airports = None
def list_ambiguous_airports():
    global _list_ambiguous_airports
    if _list_ambiguous_airports:
        return _list_ambiguous_airports
    lg.warning("list ambiguous airports!")
    _list_ambiguous_airports = set(map(itemgetter("name"),
                   Airport.objects.values('name').annotate(count=Count('pk')).order_by().filter(count__gt=1)))
    return _list_ambiguous_airports


def disambiguate(o, ambiguous=None):
    ret = set()
    if ambiguous and o.name in ambiguous:
        if o.country:
            ret.add(o.country.code)
            if o.country.name:
                ret.add(o.country.name)
                ret |= alternate_names_list(o.country)
            if o.stateCode:
                ret.add(o.stateCode)
                state = get_or_none(State, country=o.country, stateCode=o.stateCode)
                if state and state.name:
                    ret.add(state.name)
    return ret
