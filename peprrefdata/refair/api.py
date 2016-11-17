from tastypie import fields, utils
from tastypie.resources import ModelResource
from models import *
from tastypie.resources import ALL, ALL_WITH_RELATIONS


class LightAirlineResource(ModelResource):
    class Meta:
        queryset = Airline.objects.all()
        resource_name = "airline"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "code": ALL_WITH_RELATIONS,
            "name": ALL_WITH_RELATIONS,
            "alliance": ALL_WITH_RELATIONS,
        }


class AllianceResource(ModelResource):
    airlines = fields.ToManyField(LightAirlineResource, 'airline_set', full=False)
    class Meta:
        queryset = Alliance.objects.all()
        resource_name = "alliance"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "name": ALL_WITH_RELATIONS,
        }


class LightAllianceResource(ModelResource):
    class Meta:
        queryset = Alliance.objects.all()
        resource_name = "alliance"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "name": ALL_WITH_RELATIONS,
        }


class AirlineResource(ModelResource):
    alliance = fields.ForeignKey(LightAllianceResource, 'alliance', null=True, full=True)
    class Meta:
        queryset = Airline.objects.all()
        resource_name = "airline"
        allowed_methods = [ 'get' ]
        always_return_data = True
        filtering = {
            "code": ALL_WITH_RELATIONS,
            "name": ALL_WITH_RELATIONS,
            "alliance": ALL_WITH_RELATIONS,
        }

