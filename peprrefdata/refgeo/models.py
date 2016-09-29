from django.db import models
import logging
lg = logging.getLogger(__name__)


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

class Continent(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    geonameId = models.IntegerField(max_length=10, db_index=True, default=0)
    en_name = models.TextField()

class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    code3 = models.CharField(max_length=3, null=True, default=None)
    name = models.TextField()
    alternateNames = models.TextField(default='')
    capitalCode = models.CharField(max_length=3)
    currency = models.CharField(max_length=3, null=True, default=None)
    geonameId = models.IntegerField(max_length=10,db_index=True,default=0)
    population = models.IntegerField(max_length=9, default=0)
    continentCode = models.CharField(max_length=2, default="")

    def getuid(self):
        return 'c/%s'%(self.code)

    @property
    def name(self):
        return self.en_name

    @name.setter
    def name(self, value):
        self.en_name = value


class State(models.Model):
    country = models.ForeignKey(Country, null=True, blank=True)
    stateCode = models.CharField(max_length=6) # some strange states have 6 letters !
    name = models.TextField()

    class Meta:
        unique_together = ("country", "stateCode")

    @property
    def countryCode(self):
        return self.country_id

class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    prec = models.IntegerField(max_length=4, default=2)
    name = models.CharField(max_length=64, null=True, default=None)
    html = models.CharField(max_length=8, null=True, default=None)
    one_dollar = models.FloatField(null=True)

    def rate(self, other):
        """
        How much is one self worth of other
        """
        if self.code == 'USD':
            return other.one_dollar
        if other.code == 'USD':
            return 1.0 / self.one_dollar
        if self.one_dollar and other.one_dollar:
            return other.one_dollar / self.one_dollar
        else:
            raise ValueError('Conversion impossible. Rate$ self: %s. \
                Rate$ other: %s' % (str(self.one_dollar), str(other.one_dollar) ))


class Geoname(models.Model):
    geonameId = models.IntegerField(max_length=11, primary_key=True)
    name = models.TextField()
    alternateNames = models.TextField(default='')
    fcode = models.CharField(max_length=6)
    country = models.ForeignKey(Country, null=True, blank=True)
    stateCode = models.CharField(max_length=6, db_index=True, null=True) # some strange states have 6 letters !
    timezone = models.TextField(null=True)
    lat = models.FloatField()
    lng = models.FloatField()
    population = models.IntegerField(max_length=9, default=0)

    def __str__(self):
        return "%d\t%s" % (self.geonameId, self.englishName)

    @property
    def name(self):
        return self.englishName

    @name.setter
    def name(self, value):
        self.englishName = value

    def getuid(self):
        return 'g/%d' % (self.geonameId)

    @property
    def countryCode(self):
        return self.country_id

class City(models.Model):
    cityCode = models.CharField(max_length=3, primary_key=True)
    geoname = models.ForeignKey(Geoname, null=True, blank=True)
    stateCode = models.CharField(max_length=6, db_index=True) # some strange states have 6 letters !
    country = models.ForeignKey(Country, null=True, blank=True)
    name = models.TextField()
    alternateNames = models.CharField(max_length=10000, default='')
    timezone = models.TextField(null=True)
    gmt_offset = models.FloatField(null=True)
    dst_offset = models.FloatField(null=True)
    raw_offset = models.FloatField(null=True)
    precipitations = models.TextField(null=True)
    temperatures = models.TextField(null=True)
    lat = models.FloatField()
    lng = models.FloatField()
    koppen = models.CharField(max_length=3, null=True, blank=True)
    population = models.IntegerField(max_length=9, default=0, db_index=True)
    page_rank = models.FloatField(max_length=10, default=0)

    def __str__(self):
        return "%s\t%d\t%s" % (self.cityCode, self.geonameId, self.englishName)

    @property
    def name(self):
        return self.englishName

    @property
    def countryCode(self):
        return self.country_id

    def getuid(self):
        return 'g/%d' % (self.geonameId)

    @property
    def geonameId(self):
        return self.geoname.geonameId if self.geoname else 0
    @geonameId.setter
    def geonameId(self, value):
        self.geoname = get_or_none(Geoname, pk=value)



class Airport(models.Model):
    iataCode = models.CharField(max_length=3, primary_key=True)
    icao_code = models.CharField(max_length=4, null=True, default=None)
    location_type = models.CharField(max_length=4, null=True, blank=True)
    is_airport = models.BooleanField(default=False) # is really an airport ? or an "all airport" ?
    all_airports = models.BooleanField(default=False) # is really an airport ? or an "all airport" ?
    geoname = models.ForeignKey(Geoname, null=True, blank=True)
    name = models.TextField()
    alternateNames = models.CharField(max_length=10000, default='')
    timezone = models.TextField(null=True)
    stateCode = models.CharField(max_length=6, db_index=True) # some strange states have 6 letters !
    country = models.ForeignKey(Country, null=True, blank=True)
    cityCode = models.CharField(max_length=3, db_index=True)
    cityName = models.TextField()
    lat = models.FloatField()
    lng = models.FloatField()
    page_rank = models.FloatField(max_length=10, default=0)

    def __str__(self):
        return "%s\t%d\t%s" % (self.iataCode, self.geonameId, self.englishName)

    @property
    def name(self):
        return self.englishName

    def getuid(self):
        return 'g/%d' % (self.geonameId)

    def getCityAirport(self):
        if self.all_airports:
            return self
        return get_or_default(Airport, self, all_airports=True, iataCode=self.cityCode)

    @property
    def countryCode(self):
        return self.country_id

