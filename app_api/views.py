#--IMPORTS---------------------------------------------------

# import MODULES
import json
import requests

# import specific NAMES of MODULES
from django.core import serializers
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

# import LOCAL modules
from .models import Shipment, Address, Van
from .utils import getLatLng, saveToDB



#--CLASSES, FUNCTIONS etc. ---------------------------------------------------

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
