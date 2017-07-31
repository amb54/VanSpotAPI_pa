#--IMPORTS---------------------------------------------------

# import MODULES
import json
import numpy as np
import requests

# import specific NAMES of MODULES
from django.forms.models import model_to_dict
from django.utils import timezone
from sklearn.cluster import KMeans

# import LOCAL modules
from .models import Shipment, Address, Van



#--CLASSES, FUNCTIONS etc. ---------------------------------------------------
BASIC_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address='

def getLatLng(addresses):
    '''
    Loop through the list, and get the lat/long for each address.
    '''
    addresses_location = []
    for address in addresses:
        url = BASIC_URL + address + 'Seattle'
        r = requests.get(url)
        rjson = json.loads(r.content)
        if rjson['status'] == 'OK':
            location = rjson['results'][0]['geometry']['location']
            location['address'] = address
            addresses_location.append(location)
    print('Print addresses_location: %s' % addresses_location)
    return addresses_location

def saveToDB(addresses_location):
    '''
    Calculate the k-means results and save to database
    '''
    coordiantes = []
    for addr in addresses_location:
        coord = [addr['lat'], addr['lng']]
        coordiantes.append(coord)

    X = np.array(coordiantes)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    # create/save a SHIPMENT
    shipment = Shipment()
    shipment.save()
    print('Print shipment: %s' % model_to_dict(shipment))

    # crate VANS belonging to the SHIPMNET
    van0 = shipment.van_set.create(lat = centers[0][0], lng = centers[0][1])
    van1 = shipment.van_set.create(lat = centers[1][0], lng = centers[1][1])
    van2 = shipment.van_set.create(lat = centers[2][0], lng = centers[2][1])

    #array of address-objects belonging to each of the VANS
    addresses0 = []
    addresses1 = []
    addresses2 = []

    for ind in range(0,len(labels)):
        if labels[ind] == 0: # belonging to van0
            a0 = van0.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )
            addresses0.append(model_to_dict(a0))
        if labels[ind] == 1:
            a1 = van1.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )
            addresses1.append(model_to_dict(a1))
        if labels[ind] == 2:
            a2 = van2.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )
            addresses2.append(model_to_dict(a2))


    vans = [model_to_dict(van0),model_to_dict(van1),model_to_dict(van2)]
    addresses = [addresses0, addresses1, addresses2]

    # summary = {'shipment': model_to_dict(shipment),'vans': model_to_dict(van0), 'van1': model_to_dict(van1),'van2': model_to_dict(van2), 'addresses0': addresses0, 'addresses1': addresses1, 'addresses2': addresses2}
    summary = {'shipment': model_to_dict(shipment), 'vans': vans, 'addresses': addresses}
    print('Print SUMMARY---------: %s' % summary)
    return summary
