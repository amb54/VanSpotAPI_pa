#--IMPORTS---------------------------------------------------

# import MODULES
import datetime

# import specific NAMES of MODULES
from django.db import models
from django.utils import timezone

# import LOCAL modules



#--CLASSES, FUNCTIONS etc. ---------------------------------------------------
# Create your models here.

class Shipment(models.Model):
    created_date = models.DateTimeField(default=timezone.now)


class Van(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    lat = models.FloatField()
    lng = models.FloatField()

    def info_hash(self):
        ih = {'id': pk, 'shipment_id': shipment.id, 'lat': lat, 'lng': lng}


class Address(models.Model):
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    address = models.TextField()
    lat = models.FloatField()
    lng = models.FloatField()
