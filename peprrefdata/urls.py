import views
from django.conf.urls import patterns, url
from tastypie.api import Api
from refair.api import *
from refgeo.api import *
from django.conf.urls import patterns, include, url
import autocomplete.views

api = Api(api_name="refdata")
api.register(CurrencyResource())
api.register(CountryResource())
api.register(AllianceResource())
api.register(AirlineResource())
api.register(AirportResource())

urlpatterns = patterns('',
    url(r'', include(api.urls)),
    url(r'^autocomplete/?$', autocomplete.views.autocomplete, name="autocomplete")
)
