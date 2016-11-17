#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
import json, requests, logging
from trie import mk_tries, lookup, load_tries, save_tries, BadParameterError, flatten
from trie_conf import build_conf, common_name_extractor

lg = logging.getLogger(__name__)

class Spy():
    def __init__(self, func):
        self.func = func
        self.callcount = 0
    def __call__(self, *args, **kwargs):
        self.callcount += 1
        return self.func(*args, **kwargs)

class AutocompleteTrieTest(TestCase):
    fixtures = ['autocomplete.json']

    def test_common_key_extractor(self):
        class Dummy(object):
            pass
        o = Dummy()
        o.name = "Test d'azur  the strånge char foo-bar"
        ret = common_name_extractor(o, 'name')
        self.assertEquals(ret, ['test', 'azur', 'strange', 'char', 'foo', 'bar'])

    def test_flatten(self):
        self.assertEquals(flatten([[1], [2], [3]]), [1, 2, 3])

    def test_make_tries(self):
        spy = Spy(lambda i: i)
        conf = {
            'test': {
                'obj_list': lambda: [{'pk':t} for t in ['ski', 'bike', 'climbing', 'climate']],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': spy,
                'cmp_key_fn': lambda o: (o['pk'])
            }
        }
        tries = mk_tries(conf)
        trie_idx, trie_trie = tries['test']
        self.assertEquals(spy.callcount, 4)
        self.assertEquals(lookup(tries, 'ski', 'test'),
                          ([{'pk': 'ski', '_type': 'test'}], None))
        self.assertEquals(lookup(tries, 'cli', 'test'),
                          ([{'pk': 'climate', '_type': 'test'},
                            {'pk': 'climbing', '_type': 'test'}], None))

    def test_lookup(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'nice', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE' and res[0]['_type'] == 'airport')
        res, rest = lookup(tries, 'azur', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'nice cote azur', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'Nice', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'NCE', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'nce', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'paris', 'airport')
        self.assertTrue(len(res) == 0)

    def test_lookup_simple(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'nice', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE' and res[0]['_type'] == 'airport')

    def test_lookup_middle_word(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'azur', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')

    def test_lookup_multi_word(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'nice cote azur', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')

    def test_lookup_case(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'Nice', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')

    def test_lookup_iata(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'NCE', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        res, rest = lookup(tries, 'nce', 'airport')
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')

    def test_lookup_not_existent(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'paris', 'airport')
        self.assertTrue(len(res) == 0)

    def test_rest(self):
        tries = mk_tries(build_conf())
        res, rest = lookup(tries, 'nice to paris', 'airport', rest=True)
        self.assertTrue(len(res) == 1 and res[0]['pk'] == 'NCE')
        self.assertTrue(rest == 'to paris')
        with self.assertRaises(BadParameterError):
            lookup(tries, 'nice to paris', 'airport|geoname', rest=True)

    def test_limit(self):
        n_letters = ord('z') - ord('a') + 1
        keys_gen = lambda prefix: (prefix + chr(ord('a')+i) for i in range(n_letters))
        conf = {
            'testA': {
                'obj_list': lambda: [{'pk':t} for t in keys_gen('commonA')],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: (o['pk'])
            },
            'testB': {
                'obj_list': lambda: [{'pk':t} for t in keys_gen('commonB')],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: (o['pk'])
            }

        }
        tries = mk_tries(conf)
        tests = [(None, n_letters, 'testA'), (10, 10, 'testA'), (1, 1, 'testA'),
                 (None, 52, 'testA|testB'), (10, 10, 'testA|testB')]
        for limit, expected,qt in tests:
            res, rest = lookup(tries, 'common', qt, limit=limit)
            self.assertEquals(len(res), expected, "problem with test %r" % [limit,expected,qt])

    def test_sorted(self):
        n_letters = ord('z') - ord('a') + 1
        keys_gen = ('common' + chr(ord('a')+i) for i in range(n_letters))
        conf = {
            'test': {
                'obj_list': lambda: [{'pk':t} for t in keys_gen],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: o['pk']
            }
        }
        tries = mk_tries(conf)
        res, rest = lookup(tries, 'common', 'test')
        cmp_key_fn = conf['test']['cmp_key_fn']
        all(cmp_key_fn(a)<cmp_key_fn(b) for a,b in zip(res, res[1:]))

    def test_priority(self):
        n_letters = ord('z') - ord('a') + 1
        conf = {
            'test_prio': {
                'obj_list': lambda: [{'pk':t} for t in ['ski', 'bike', 'climbing', 'climate']],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: o['pk']
            },
            'test': {
                'obj_list': lambda: [{'pk':t} for t in ['ski', 'bike', 'climbing', 'climate']],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: o['pk']
            }
        }
        tries = mk_tries(conf)
        res, rest = lookup(tries, 'ski', 'test_prio|test')
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0]['_type'], 'test_prio')
        res, rest = lookup(tries, 'ski', 'test|test_prio')
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0]['_type'], 'test')

    def test_dump(self):
        n_letters = ord('z') - ord('a') + 1
        conf = {
            'test_prio': {
                'obj_list': lambda: [{'pk':t} for t in ['ski', 'bike', 'climbing', 'climate']],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: o['pk']
            },
            'test': {
                'obj_list': lambda: [{'pk':t} for t in ['ski', 'bike', 'climbing', 'climate']],
                'extract_terms': lambda i: [unicode(i['pk'])],
                'extract_key': lambda i: bytes(i['pk']),
                'mk_obj': lambda i: i,
                'cmp_key_fn': lambda o: o['pk']
            }
        }
        tries = mk_tries(conf)
        from tempfile import NamedTemporaryFile
        fname = NamedTemporaryFile(prefix='testTrie', dir='/tmp/', delete=False).name
        res, rest = lookup(tries, 'ski', 'test_prio|test')
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0]['_type'], 'test_prio')
        save_tries(tries, fname)
        tries = load_tries(fname)
        res, rest = lookup(tries, 'ski', 'test_prio|test')
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0]['_type'], 'test_prio')
