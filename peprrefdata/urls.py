import views
from django.conf.urls import patterns, url
from tastypie.api import Api
from refgeo.api import CurrencyResource
from django.conf.urls import patterns, include, url

api = Api(api_name="refdata")
api.register(CurrencyResource())

urlpatterns = patterns('',
    url(r'', include(api.urls)),
)
