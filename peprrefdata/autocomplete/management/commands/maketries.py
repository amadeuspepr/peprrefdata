from django.core.management.base import BaseCommand, CommandError
from autocomplete.trie import mk_tries, save_tries
from autocomplete.trie_conf import build_conf, TRIES_FNAME
import logging

lg = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Create tries and save them to file according to configuration"
    def handle(self, *args, **kwargs):
        lg.info("Make tries")
        tries = mk_tries(build_conf())
        lg.info("Tries created")
        save_tries(tries, TRIES_FNAME)
