from objects import make_airport_obj, make_country_obj, make_city_obj, make_geoname_obj, make_activity_obj
from objects import city_get_keys, airport_get_keys, geoname_get_keys, country_get_keys, activity_get_keys
# from autocomplete import airports_with_guide, cities_with_subway
from peprrefdata.autocomplete.ambiguous import list_ambiguous_cities, list_ambiguous_airports, list_ambiguous_geonames
from peprrefdata.refgeo.models import Airport, City, Geoname, Country
# from backend.apps.images.models import Index as ImageIndex
from peprrefdata import asciiname
# from Stemmer import Stemmer
from django.db.models import Q
import re
blacklist_words = set(['d', 'the'])
common_name_extractor = lambda i, attr: [unicode(asciiname(part.lower()))
                                        for part in re.split('[ \-\']+', getattr(i, attr, ''))
                                        if part.lower() not in blacklist_words]
def wrap_obj_maker(base_fn, keys_fn, **kwargs):
    """object is constructed with base_fn. later we add a keys property by
    calling keys_fn"""
    def _inner(model_obj):
        o = base_fn({}, model_obj, **kwargs)
        o['keys'] = "|".join(keys_fn(model_obj, **kwargs))
        return o
    return _inner

# airport query
q1 = Q(is_airport=True) & Q(icao_code__isnull=False) & (~Q(icao_code__exact=""))
q2 = Q(all_airports=True)

def no_cache_wrapper(func):
    "use this to wrap make function that do not take cache argument"
    def _inner(_, *args, **kwargs):
        return func(*args, **kwargs)
    return _inner
# trie construction configuration
# obj_list: function returning the list of model objects to index
# extract_key: function starting from a model object, returns a list of string
#              to be used as index
# mk_obj: function used to build object to be sent over the wire
# cmp_key_fn [Obj -> Tuple]: function that, given a final object, returns a tuple
#                            that will be used as "key" parameter in python
#                            standard "sorted" function. Sort order is not
#                            specified but can be configured with - signs.
# TODO
# - index alternate names?
def nocache(qs):
#     from caching.base import NO_CACHE
#     qs.timeout = NO_CACHE
    return qs

from django.conf import settings
import os
TRIES_FNAME = os.path.join(settings.APP_DIR, '/tmp/peprrefdata/tries.data')


def build_conf():
    return {
        'airport': {
            'obj_list': lambda: nocache(Airport.objects.filter(q1|q2)),
            'extract_terms': lambda i: common_name_extractor(i, 'name') + [i.pk.lower()] +
                common_name_extractor(i, 'cityName'),
            'extract_key': lambda i: i.pk,
            'mk_obj': wrap_obj_maker(make_airport_obj, airport_get_keys,
                                     lgfilter=True,
                                     ambiguous=list_ambiguous_airports()),
            'cmp_key_fn': lambda o: (-o.get('order', 0), o['semantic']),
        },
#         'geoname': {
#             'obj_list': lambda: nocache(Geoname.objects.all()),
#             'extract_terms': lambda i: common_name_extractor(i, 'name'),
#             'extract_key': lambda i: i.pk,
#             'mk_obj': wrap_obj_maker(make_geoname_obj, geoname_get_keys,
#                                      lgfilter=True,
#                                      ambiguous=list_ambiguous_geonames()),
#             'cmp_key_fn': lambda o: (-o.get('order', 0), o.get('name')),
#         },
#         'airport-guide': {
#             'obj_list': lambda: nocache(Airport.objects.filter(iataCode__in=airports_with_guide)),
#             'extract_terms': lambda i: common_name_extractor(i, 'name') + [i.pk],
#             'extract_key': lambda i: i.pk,
#             'mk_obj': wrap_obj_maker(make_airport_obj, airport_get_keys,
#                                      lgfilter=True,
#                                      ambiguous=list_ambiguous_airports()),
#             'cmp_key_fn': lambda o: (-o.get('order', 0), o['semantic']),
#         },
#         'subway': {
#             'obj_list': lambda: nocache(City.objects.filter(cityCode__in=cities_with_subway)),
#             'extract_terms': lambda i: common_name_extractor(i, 'name'),
#             'extract_key': lambda i: i.pk,
#             'mk_obj': wrap_obj_maker(make_city_obj, city_get_keys,
#                                      include_country=True, lgfilter=True,
#                                      ambiguous=list_ambiguous_cities()),
#             'cmp_key_fn': lambda o: (-o.get('order', 0), o.get('name')),
#         },
        'country': {
            'obj_list': lambda: nocache(Country.objects.all()),
            'extract_terms': lambda i: common_name_extractor(i, 'name'),
            'extract_key': lambda i: i.pk,
            'mk_obj': wrap_obj_maker(no_cache_wrapper(make_country_obj), country_get_keys,
                                     lgfilter=True),
            'cmp_key_fn': lambda o: (-o.get('population', 0), o.get('name')),
        },
#         'tag': {
#             'obj_list': lambda: [{'pk':t} for t in ImageIndex(None).tags],
#             'extract_terms': lambda i: [i['pk']] + \
#             [part.lower() for part in re.split('[ -]+', i['pk'])[1:]],
#             'extract_key': lambda i: i['pk'],
#             'mk_obj': lambda o: o,
#             'cmp_key_fn': lambda o: (o.get('pk', 0), )
#         },
#         'activity': {
#             'obj_list': lambda: nocache(Activity.objects.all()),
#             'extract_terms': lambda i: common_name_extractor(i, 'name'),
#             'extract_key': lambda i: i.pk,
#             'mk_obj': wrap_obj_maker(no_cache_wrapper(make_activity_obj), activity_get_keys,
#                                      lgfilter=True, stemmers={'en': Stemmer('english')}),
#             'cmp_key_fn': lambda o: (-o.get('order', 0), o.get('name')),
#         }
    }
