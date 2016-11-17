from django.db import models


class Alliance(models.Model):
    name = models.TextField()
 
class Airline(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    code3 = models.CharField(max_length=3, null=True, default=None)
    name = models.TextField()
    alliance = models.ForeignKey(Alliance, null=True, default=None)
    alliance_status = models.TextField(null=True, default=None)
