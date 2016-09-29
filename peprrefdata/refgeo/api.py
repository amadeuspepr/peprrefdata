from tastypie import fields, utils
from tastypie.resources import ModelResource
from models import Currency
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
