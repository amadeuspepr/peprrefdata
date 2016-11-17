from jsonview.decorators import json_view
from django.http import HttpResponseBadRequest
import logging

lg = logging.getLogger(__name__)

TRIES = None

def prepare_tries():
    global TRIES
    if not TRIES:
        lg.info("autocomplete: loading tries")
        try:
            from trie import load_tries
            from trie_conf import TRIES_FNAME
            TRIES = load_tries(TRIES_FNAME)
            lg.info("autocomplete: tries loaded from file")
        except IOError:
            from trie import mk_tries, save_tries
            from trie_conf import build_conf
            from trie_conf import TRIES_FNAME
            lg.info("autocomplete: tries not found, building them")
            TRIES = mk_tries(build_conf())
            lg.info("autocomplete: tries generated")
            save_tries(TRIES, TRIES_FNAME)



@json_view
def autocomplete(request):
    from trie import lookup, BadParameterError
    prepare_tries()
    searched_texts = request.GET.get('term')
    req_types = request.GET.get('type')
    limitn = request.GET.get('limit',10)
    try:
        limit = min(30,int(limitn))
    except:
        limit = 10
    (found_list, rest) = lookup(request, TRIES, searched_texts, req_types)
    if found_list is None:
        return HttpResponseBadRequest()
    return {'response' : found_list }
