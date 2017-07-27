from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.forms.models import model_to_dict

from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers

import requests
import numpy as np
from sklearn.cluster import KMeans


# Create your views here.
from django.utils import timezone
from .models import Shipment, Address, Van

BASIC_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address='

@csrf_exempt
def centers(request):
    if request.method == 'POST':
            # 1. Use the `request` variable to get the
            # addresses list.
        body_unicode = request.body
        # body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        addresses = body['addresses']
        address = addresses[0]
        print('Print addresses: %s' % addresses)
        # print(len(addresses))
        # print('Raw Data: "%s"' % request.body)

            # 2. Loop through the list, and get the lat/long
            # for each address.
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
             # 3. Here you calculate the k-means results
        coordiantes = []
        for addr in addresses_location:
            coord = [addr['lat'], addr['lng']]
            coordiantes.append(coord)
        X = np.array(coordiantes)
        kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_



            # 4. Return centers as list of lat/long pairs  jason respose in django
        print('Print centers: %s' % centers)

        centers_dict = {
            'center1': {'lat': centers[0][0], 'lng': centers[0][1]},
            'center2': {'lat': centers[1][0], 'lng': centers[1][1]},
            'center3': {'lat': centers[2][0], 'lng': centers[2][1]},
        }
        print('Print centers_dict: %s' % centers_dict)


        shipment = Shipment()
        shipment.save()
        van0 = shipment.van_set.create(lat = centers[0][0], lng = centers[0][1])
        van1 = shipment.van_set.create(lat = centers[1][0], lng = centers[1][1])
        van2 = shipment.van_set.create(lat = centers[2][0], lng = centers[2][1])

        for ind in range(0,len(labels)):
            if labels[ind] == 0:
                van0.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )
            if labels[ind] == 1:
                van1.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )
            if labels[ind] == 2:
                van2.address_set.create(lat = addresses_location[ind]['lat'],lng = addresses_location[ind]['lng'],address = addresses_location[ind]['address'] )

        summary = {'shipment': model_to_dict(shipment),'van0': model_to_dict(van0), 'van1': model_to_dict(van1),'van2': model_to_dict(van2)}
        # return JsonResponse(model_to_dict(shipment))
        return JsonResponse(summary)
    return HttpResponse("Not an POST request")

@csrf_exempt
def newShipment(request):
    '''
    Use the `request` variable to get the addresses list.
    '''
    if request.method == 'POST':
        body_unicode = request.body
        # body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        addresses = body['addresses']
        print('Print addresses: %s' % addresses)
        # print(len(addresses))
        # print('Raw Data: "%s"' % request.body)

        addresses_location = getLatLng(addresses)
        summary = saveToDB(addresses_location)
        return JsonResponse(summary)

    return HttpResponse("Not an POST request")


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

@csrf_exempt
def shipments(request):
    shipmentsList = []
    allShiments = Shipment.objects.all()

    for shipment in allShiments:
        shipmentSze = serializers.serialize('json', [shipment , ])
        shipmentSzeDict = json.loads(shipmentSze)[0]
        shipmentsList.append(shipmentSzeDict)
    print(shipmentsList)
    return HttpResponse(json.dumps(shipmentsList))

def shipment_detail(request, pk):
    print (pk)
    shipment = Shipment.objects.get(pk=pk)
    shipmentSze = serializers.serialize('json', [shipment , ])
    shipmentSzeDict = json.loads(shipmentSze)[0]

    vans = Van.objects.filter(shipment_id=pk)
    print('vans: %s' % vans)

    addresses_QuerySets = []
    vans_dict = []
    for ind in range(0, len(vans)):
        addresses_QuerySets.append(Address.objects.filter(van_id=vans[ind].pk))
        vans_dict.append(model_to_dict(vans[ind]))

    addresses_dict = []
    for ind in range(0, len(addresses_QuerySets)):
        add_dict = []
        for i in range(0,len(addresses_QuerySets[ind])):
            add_dict.append(model_to_dict(addresses_QuerySets[ind][i]))
        addresses_dict.append(add_dict)


    summary = {'shipment': shipmentSzeDict, 'vans': vans_dict, 'addresses': addresses_dict}

    return HttpResponse(json.dumps(summary))



def van(request):
    body_unicode = request.body
    body = json.loads(body_unicode)
    van_id = body['id']

    van = Van.objects.get(pk = van_id)
    return
