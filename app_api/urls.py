#--IMPORTS---------------------------------------------------

# import MODULES

# import specific NAMES of MODULES
from django.conf.urls import url

# import LOCAL modules
from . import views


#--CLASSES, FUNCTIONS etc. ---------------------------------------------------

urlpatterns = [
    url(r'^newshipment$', views.newShipment, name='newShipment'),
    url(r'^shipments$', views.shipments, name='shipments'),
    url(r'^shipments/(?P<pk>[0-9]+)$', views.shipment_detail, name='shipment_detail'),

]
