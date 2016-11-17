# coding: utf-8

import marisa_trie
from peprrefdata import update_in, asciiname
from itertools import izip, repeat
from functools import partial
import pickle
import copy
import os
import errno

from peprrefdata.refgeo.api import AirportResource
from peprrefdata.refgeo.models import Airport


import logging
lg = logging.getLogger(__name__)

# helper functions
flatten = lambda li: [item for sublist in li for item in sublist]

# @profile_deep("/logs/mk_tries.txt")
def mk_tries(conf):
    """Build prefix tries according to configuration. It return a
    dictionary in the form autocomplete_type -> (objs_dict, trie)

    trie is the data structure used to lookup queries, objs_dict is a
    dictionary used to maps ids stored in tries to real objects. This
    is necessary since trie cannot store arbitrary objects.
    """
    def _mk_obj(t, f, comp_fn):
        """wrapper function to add fields to objects. _type is used to
        store the table name while _cmp stores a tuple used for later
        comparison"""
        def _inner(i):
            ret = f(i)
            ret['_type'] = t
            ret['_cmp'] = comp_fn(ret)
            return ret
        return _inner
    ret = {}
    for (k,c) in conf.iteritems():
        # build obj list
        lg.debug("building trie %s", k)
        obj_list = c['obj_list']()
        # build obj dictionary.
        objs_dict = {bytes(c['extract_key'](i)): _mk_obj(k, c['mk_obj'], c['cmp_key_fn'])(i)
                     for i in obj_list}
        # build tuples to be fed into trie
        # [(term1, key), (term2, key), ..]
        tuples = [izip(c['extract_terms'](i), repeat(bytes(c['extract_key'](i))))
                  for i in obj_list]
        # build trie
        trie = marisa_trie.BytesTrie(flatten(tuples))
        ret[k] = (objs_dict, trie)
    return ret

def _lookup(trie_data, qs, rest):
    """private lookup function.
    trie_data is a tuple in the form (object_index, trie)
    qs is the query string
    rest is a boolean configuring the logic (more on that later)
    returns a tuple(list of objects matching query, rest)

    Used algorithm consists in splitting search query over spaces and iterating
    over them, reducing results by intersecting them.
    let Qi be a single word of query string result is
    lookup(Q0) ∩ lookup(Q1) ∩ .. ∩ lookup(Qn)

    When rest parameter is == True, iteration stops when a term causes
    the number of results to drop to 0. When this condition is
    reached, function returns result before the term and the rest of
    the query string.
    """
    idx, trie = trie_data
    # helper fn
    resolve = lambda xs: [idx.get(x) for x in xs]
    current_res = None
    splitted_query = [asciiname(q) for q in qs.split()]
    for (j, q) in enumerate(splitted_query):
        _q = q.lower()
        hits = set(i[1] for i in trie.items(unicode(_q)))
        # first iteration
        if current_res == None:
            stage = set(hits)
        # we already have some result, intersect with new
        else:
            stage = current_res & set(hits)
        # rest required. If last query part made number of results drop to 0,
        # consider it part of another query
        if (not stage):
            if rest:
                # handle first iteration
                if current_res == None:
                    current_res = []
                # return collected result until here + remaining terms
                return resolve(current_res), ' '.join(splitted_query[j:])
            else:
                # no need to continue
                return [], None
        current_res = stage
    return resolve(current_res), None

class BadParameterError(Exception):
    pass


def lookup(request, tries, qs, qt, limit=None, rest=False):
    """public method to query autocomplete engine.
    tries[dict]: tries data structures generated by mk_tries
    qs[string]: query string e.g. "nice"
    qt[string]: query type e.g. "airport|geoname"
    limit[int]: limit total number of results, default 10. If None, no limit is imposed
    rest[bool]: stop iterating over query string when result number drops to 0
                and return the rest of query string

    returns a tuple of (results, rest) where results is a list of objects, each
    one with a type property corresponding to autocomplete table and rest is
    the remaining part of query string when rest parameter is set to True.
    """
    ret = {}
    rests = []
    query_types = qt.split('|')
    if limit != None:
        results_per_type = limit//len(query_types)
    else:
        results_per_type = None
    # put results in a dict indexed by pk in reverse order respect to
    # query types to eliminate objects with the same key and giving
    # precedence to types that appear early in the query type
    # string. A sort of uniq with precedence
    for q in query_types[::-1]:
        if q in tries:
            res, rest = _lookup(tries[q], qs, rest)
            rests.append(rest)
            # put results into ret dict and add _type key to each element
            ret.update({o['pk']: o for o in res})
        else:
            lg.error("No such trie : %r", q)
    # now iterate over filtered results and put each of them in a
    # bucket corresponding to their type. This step is needed to sort
    # elements within their type and return them in the order
    # specified by query type.
    per_type = {}
    for o in ret.values():
        per_type.setdefault(o['_type'], []).append(o)

    if rest:
        # FIXME think about how reduce rests when multiple query
        # types.  are given (max, min, assert all equals?). For the
        # time being we raise an exception when rest == True and
        # ntypes > 1
        if len(rests) > 1:
            raise BadParameterError("rest cannot be true when multiple query type are required.")
    # return result sorted and limited. Sort leverages python
    # comparison method for tuples. _cmp field is computed and stored
    # in the object during construction.
    def rm_cmp_key(i):
        "copy object and remove _cmp key before returning it."
        ret = copy.copy(i)
        del ret['_cmp']
        return ret

    objects = map(rm_cmp_key, flatten([sorted(os, key=lambda i: i['_cmp'])[:results_per_type] for (t,os) in per_type.iteritems()]))

    def get_resource_for(obj):
        objtype = obj.get("_type")
        pk = obj.get("pk")
        if objtype == 'airport':
            res = AirportResource()
            return res.build_bundle(request=request, obj=Airport.objects.get(pk=pk))
        return obj

    return (map(get_resource_for, objects),
            reduce(lambda acc, i: acc, rests))

# Tries load/save helper functions
def load_tries(fname):
    lg.info("Loading trie from %s",fname)
    with open(fname) as f:
        return pickle.load(f)

def save_tries(tries, fname):
    lg.info("Save trie in %s [%s]",fname, os.path.dirname(fname))
    dirname = os.path.dirname(fname)
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
             raise
    with open(fname, 'wb') as f:
        pickle.dump(tries, f)
