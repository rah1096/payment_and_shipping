from django.shortcuts import render, render_to_response, HttpResponse
from django.template.context import RequestContext
from django.conf import settings
import stripe, json, csv, os
from .models import Item

#ups
from ups import errors
from ups.api.package_rates import UPSRateRequest, UPSShipment, UPSPackage, get_service_name, UPS_SERVICE_CODES
from ups.api.base import UPSConnection, UPS_CONNECTION_TEST

#fedex
from fedex.config import FedexConfig
from fedex.services.rate_service import FedexRateServiceRequest




def charge_card(request):
    request_context = RequestContext(request)
    context = {'request': request}

    stripe.api_key = settings.STRIPE_API_KEY

    context['request_post'] = request.POST

    context['json_format'] = json.dumps(request.POST)

    if request.method == "POST":
        try:
            stripe_token = stripe.Token.create(
                card={
                    "number": request.POST.get('number'),
                    "exp_month": request.POST.get('month'),
                    "exp_year": request.POST.get('year'),
                    "cvc": request.POST.get('cvc')
                },
            )

            stripe_charge = stripe.Charge.create(
                amount=request.POST.get('amount'),
                currency="usd",
                source=stripe_token.get('id'),
                description="Charge for test@example"
            )

            context['order_status'] ="Thank you!"
        except (stripe.CardError, stripe.InvalidRequestError), e:
            "There was an error"
            context['order_status'] = e

    if request.method == "GET":
        context['stripe_token'] = "Please place an order!"
        # context['stripe_charge'] = stripe_charge

    return render_to_response('index.html', context, context_instance=request_context)

def read_csv(request):
    request_context = RequestContext(request)
    context = {'request': request}

    # os_path = os.path.dirname(__file__)
    # os_path2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # os_path3 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # print os_path2
    #
    # alt_csv_file_path = "%s/csv_files/Amazon.csv" % os.path.dirname(os.path.abspath(__file__))

    csv_file_path = "%s/Amazon.csv" % os.path.dirname(os.path.abspath(__file__))

    csv_file = open(csv_file_path, 'r')
    line = 0
    try:
        reader = csv.reader(csv_file)
        print dir(reader)
        for row in reader:
            item_id = row[0]
            title = row[1]
            description = row[2]
            manu = row[3]
            try:
                price = float(row[4])
            except:
                print "Failed conversion %s %s" % (line, row[4])
                price = 0

            new_item = Item()
            new_item.item_id = item_id
            new_item.title = title
            new_item.description = description
            new_item.manufacturer = manu
            new_item.price = price
            try:
                new_item.save()
            except Exception, e:
                print e
                pass

            line = line + 1
            # print line

    finally:
        csv_file.close()

    # context['os_path'] = os_path
    # context['os_path2'] = os_path2
    # context['os_path3'] = os_path3
    return render_to_response('csv.html', context, context_instance=request_context)

#<=====template view======>
def item_list_view(request):
    request_context = RequestContext(request)

    context = {'request': request}

    items = Item.objects.all()

    context['items'] = items

    return render_to_response('item_list.html', context, context_instance=request_context)

#<======json serialized view========>
def json_item_list(request):
    all_items = []
    json_object = {}

    items = Item.objects.all()

    item_num = 0
    for item in items:
        json_object[item_num] = {}

        json_object['title'] = item
        json_object['item_id'] = item.item_id
        json_object['description'] = item.description
        json_object['manufacturer'] = item.manufacturer
        json_object['price'] = "%s" % item.price

        all_items.append(json_object[item_num])
        item_num += 1

    return HttpResponse(json.dumps(all_items))


def ups_shipping(request):
    request_context = RequestContext(request)
    context = {'request': request}

    weight = 2.0

    connection = UPSConnection(settings.UPS_USER_ID,
                               settings.UPS_USER_PWD,
                               settings.UPS_ACCESS_KEY,
                               UPS_CONNECTION_TEST
                               )

    package = UPSPackage(weight=weight)

    ship_to = {
        'address':{
            'zip':'84003',
            'country':'US',
            'city':'Provo'
        }
    }

    shipment = UPSShipment(settings.SHIPPER_OBJECT, ship_to, [package])

    ups_rate_req = UPSRateRequest(shipment)

    ups_rate = connection.execute(ups_rate_req)

    context['ups_rate'] = json.dumps(ups_rate)

    shipping_options = []

    for row in ups_rate['RatedShipment']:
        shipping_options.append({
            'option':UPS_SERVICE_CODES[row['Service']['Code']],
            'price':row['TotalCharges']['MonetaryValue'],
            'code':row['Service']['Code'],
        })

    context['shipping_options'] = shipping_options

    return render_to_response('ups.html', context, context_instance=request_context)

def fedex_shipping(request):
    request_context = RequestContext(request)
    context = {'request': request}

    fedex_config = FedexConfig(key=settings.FEDEX_KEY,
                               password=settings.FEDEX_PASSWORD,
                               account_number=settings.FEDEX_ACCOUNT_NUMBER,
                               meter_number=settings.FEDEX_METER_NUMBER,
                               integrator_id=settings.FEDEX_INTEGRATOR_ID,
                               express_region_code=settings.FEDEX_EXPRESS_REGION_CODE,
                               use_test_server=True,
                               )

    fedex_ship_types = {}
    shipping_types = [
        (01, "PRIORITY_OVERNIGHT", "FedEx Priority Overnight"),
        (02, "PRIORITY_OVERNIGHT_SATURDAY_DELIVERY", "FedEx Priority Overnight Saturday Delivery"),
        (03, "FEDEX_2_DAY", "FedEx 2 Day"),
        (04, "FEDEX_2_DAY_SATURDAY_DELIVERY", "FedEx 2 Day Saturday Delivery"),
        (05, "STANDARD_OVERNIGHT", "FedEx Standard Overnight"),
        (06, "FIRST_OVERNIGHT", "FedEx First Overnight"),
        (07, "FIRST_OVERNIGHT_SATURDAY_DELIVERY", "FedEx First Overnight Saturday Delivery"),
        (08, "FEDEX_EXPRESS_SAVER", "FedEx Express Saver"),
        (09, "FEDEX_1_DAY_FREIGHT", "FedEx 1 Day Freight"),
        (10, "FEDEX_1_DAY_FREIGHT_SATURDAY_DELIVERY", "FedEx 1 Day Freight Saturday Delivery"),
        (11, "FEDEX_2_DAY_FREIGHT", "FedEx 2 Day Freight"),
        (12, "FEDEX_2_DAY_FREIGHT_SATURDAY_DELIVERY", "FedEx 2 Day Freight Saturday Delivery"),
        (13, "FEDEX_3_DAY_FREIGHT", "FedEx 3 Day Freight"),
        (14, "FEDEX_3_DAY_FREIGHT_SATURDAY_DELIVERY", "FedEx 3 Day Freight Saturday Delivery"),
        (15, "INTERNATIONAL_PRIORITY", "FedEx International Priority"),
        (16, "INTERNATIONAL_PRIORITY_SATURDAY_DELIVERY", "FedEx International Priority Saturday Delivery"),
        (17, "INTERNATIONAL_ECONOMY", "FedEx International Economy"),
        (18, "INTERNATIONAL_FIRST", "FedEx International First"),
        (19, "INTERNATIONAL_PRIORITY_FREIGHT", "FedEx International Priority Freight"),
        (20, "INTERNATIONAL_ECONOMY_FREIGHT", "FedEx International Economy Freight"),
        (21, "GROUND_HOME_DELIVERY", "FedEx Ground Home Delivery"),
        (22, "FEDEX_GROUND", "FedEx Ground"),
        (23, "INTERNATIONAL_GROUND", "FedEx International Ground"),
        (24, "SMART_POST", "FedEx SmartPost"),
        (25, "FEDEX_FREIGHT_PRIORITY", "FedEx Freight Priority"),
        (26, "FEDEX_FREIGHT_ECONOMY", "FedEx Freight Economy"),
    ]

    print shipping_types[1]

    for (x,y,z) in shipping_types:
        print "shipping # %s" % x
        print "shipping code: %s" % y
        print "shipping desc: %s" % z


    rate_request = FedexRateServiceRequest(fedex_config)

    rate_request.RequestedShipment.DropoffType = 'REGULAR_PICKUP'
    rate_request.RequestedShipment.ServiceType = shipping_types[6][1]
    rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'
    #rate_request.RequestedShipment.PackageDetail = 'INDIVIDUAL_PACKAGES'

    rate_request.RequestedShipment.Shipper.Address.PostalCode = '84604'
    rate_request.RequestedShipment.Shipper.Address.CountryCode = 'US'
    rate_request.RequestedShipment.Shipper.Address.Residential = True

    rate_request.RequestedShipment.Recipient.Address.PostalCode = '84604'
    rate_request.RequestedShipment.Recipient.Address.CountryCode = 'US'
    rate_request.RequestedShipment.EdtRequestType = 'NONE'
    rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'

    package1_weight = rate_request.create_wsdl_object_of_type('Weight')

    package1_weight.Value = 2
    package1_weight.Units = "LB"


    package1 = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
    package1.Weight = package1_weight
    package1.GroupPackageCount = 1

    package1.PhysicalPackaging = 'BOX'
    rate_request.add_package(package1)

    rate_request.send_request()

    the_response = rate_request.response.RateReplyDetails

    context['response'] = the_response

    for service in rate_request.response.RateReplyDetails:
        for detail in service.RatedShipmentDetails:
            for surcharge in detail.ShipmentRateDetail.Surcharges:
                if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                    print "%s: ODA rate_request charge %s" % (service.ServiceType, surcharge.Amount.Amount)
                    fedex = "%s: ODA rate_request charge %s" % (service.ServiceType, surcharge.Amount.Amount)
        for rate_detail in service.RatedShipmentDetails:
            print "%s: Net FedEx Charge %s %s" % (service.ServiceType, rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Currency,
            rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)

        fedex_3_day = (rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)

        context['response'] = fedex_3_day

    return render_to_response('fedex.html', context, context_instance=request_context)