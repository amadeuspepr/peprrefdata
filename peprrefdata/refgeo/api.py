from tastypie import fields, utils
from tastypie.resources import ModelResource
from models import *
from tastypie.resources import ALL, ALL_WITH_RELATIONS


class CurrencyResource(ModelResource):
    class Meta:
        queryset = Currency.objects.all()
        resource_name = "currency"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "code": ALL_WITH_RELATIONS,
            "name": ALL_WITH_RELATIONS,
        }

class CountryResource(ModelResource):
    currency = fields.ForeignKey(CurrencyResource, "currency", full=False)
    class Meta:
        queryset = Country.objects.all()
        resource_name = "country"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "code": ALL_WITH_RELATIONS,
            "name": ALL_WITH_RELATIONS,
        }


class AirportResource(ModelResource):
    country = fields.ForeignKey(CountryResource, "country", full=False)
    class Meta:
        queryset = Airport.objects.all()
        resource_name = "airport"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "code": ALL_WITH_RELATIONS,
            "name": ALL_WITH_RELATIONS,
            "country": ALL_WITH_RELATIONS,
        }