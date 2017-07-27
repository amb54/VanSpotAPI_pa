from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^shipments$', views.centers, name='centers'),
    url(r'^newshipment$', views.newShipment, name='newShipment'),
    url(r'^shipments$', views.shipments, name='shipments'),
    url(r'^shipments/(?P<pk>[0-9]+)$', views.shipment_detail, name='shipment_detail'),

]
