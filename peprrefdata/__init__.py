import unicodedata



def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def get_or_default(model, defaultvalue, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return defaultvalue


def asciiname(input_str):
    if type(input_str) == str:
        # try to encode input string into utf-8
        try:
            input_str = unicode(input_str,'utf-8')
        except:
            lg.error("Cannot transform %s into utf-8" % (repr(input_str)))
    if type(input_str) == unicode:
        return ''.join(c for c in unicodedata.normalize('NFD', input_str)
                       if unicodedata.category(c) != 'Mn').encode('ascii', 'ignore')
    return input_str

def update_in(o, kws, fn):
    """Returns a modified version of object without modifying original. This
    is accomplished through structure sharing.
    Params:
      o can be a dict or a list
      kws list of keys to select item in the nested structure. List items are
          accessed with int keys.
      fn user supplied function that will be applied on selected object
    """
    if type(o) != list and type(o) != dict:
        raise ValueError("Object type should be dict or list")
    if type(o) == list and type(kws[0]) != int:
        raise ValueError("List should be accessed with int keys")
    new_obj = copy.copy(o)
    if len(kws) == 1:
        assert ((type(new_obj) == list and type(kws[0]) == int) or
                type(new_obj) == dict)
        # in case of objects, create missing key
        try:
            new_obj[kws[0]] = fn(new_obj[kws[0]])
        except KeyError:
            new_obj[kws[0]] = fn(None)
    else:
        new_obj[kws[0]] = update_in(new_obj[kws[0]], kws[1:], fn)
    return new_obj


PSEUDO_LANG = '__'
VALID_LANGUAGES = [ PSEUDO_LANG, 'en', 'fr', 'it', 'es', 'pt', 'de' ]

def alternate_names_list(o, lgfilter=False, ambiguous=None, langs=None):
    allnames = [couple.split('@') for couple in o.alternateNames.split('|') if '@' in couple]
    if langs:
        lgfilter = True
    else:
        langs = VALID_LANGUAGES
    if lgfilter:
        allnames = filter(lambda x:x[0] in langs, allnames)
    return set(map(lambda x:asciiname(x[1]),allnames))


def getCityOrAirportCountryName(obj, countryCache=None):
    if countryCache is not None and obj.countryCode in countryCache:
        return countryCache[obj.countryCode]
    ret = obj.country.name
    if countryCache is not None:
        countryCache[obj.countryCode] = ret
    return ret
