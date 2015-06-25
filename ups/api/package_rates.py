from ups.api.base import UPSRequest, UPSElement

UPS_SERVICE_CODES = {
                     '01':'Next Day Air',
                     '02':'2nd Day Air',
                     '03':'UPS Ground',
                     '07':'UPS Express',
                     '08':'UPS Expedited',
                     '11':'UPS Standard',
                     '12':'UPS Three-Day Select',
                     '13':'UPS Saver',
                     '14':'UPS Express Early A.M.',
                     '54':'UPS Worldwide Express Plus',
                     '59':'UPS Second Day Air A.M.',
                     '65':'UPS Saver',
                     '82':'UPS Today Standard',
                     '83':'UPS Today Dedicated Courrier',
                     '84':'UPS Today Intercity',
                     '85':'UPS Today Express',
                     '86':'UPS Today Express Saver',
                     '308':'UPS Freight LTL',
                     '309':'UPS Freight LTL Guaranteed',
                     '310':'UPS Freight LTL Urgent',
                     'TDCB':'Trade Direct Cross Border',
                     'TDA':'Trade Direct Air',
                     'TDO':'Trade Direct Ocean'
                     }


def get_service_name(service_code):
    """
    Given a service code, return the human-readable name for 
    that service
    
    @return: string on success or False
    """
    return UPS_SERVICE_CODES.get(service_code, False)

class UPSRateRequest(UPSRequest):
    """
    Wrapper class for shipping rate request template
    """
    ACTION = "Rate"
    OPTION = "Shop"
    template = "rate/rate_request.xml"
    
    def __init__(self, shipment, pickup_type_code=None, customer_type_code=None, option="Shop"):
        """
        Initialize this rate request
        
        @param shipment: a UPSShipment object
        @param option: the Request option for this request choices are 'Rate' and 'Shop'
        """
        self.shipment = shipment 
        self.pickup_type_code = pickup_type_code or '01'
        self.customer_type_code = customer_type_code
        self.OPTION = option
        
    def get_context(self):
        """
        Return the context dictionary to render this 
        object's template
        
        @return: dictionary
        """
        return {'request': self}
        
        
class UPSShipment(UPSElement):
    """
    Wrapper for shipment template
    """
    template = "rate/shipment.xml"
    
    def __init__(self, shipper, ship_to, packages, service_code=None, ship_from=None, negotiated_rates=False):
        """
        @param shipper: A dictionary or object with keys - name, number, phone_number, and address
        @param ship_to: A dictionary or object with keys - name, and address
        @param packages: A list of UPSPackages
        """
        self.shipper = shipper
        self.ship_to = ship_to
        self.packages = packages
        self.service_code = service_code
        self.ship_from = ship_from
        self.negotiated_rates = negotiated_rates
        
    def get_context(self):
        """
        Return the context dictionary to render this object's
        template
        
        @return dictionary
        """
        return {'shipment':self}
    

class UPSPackage(UPSElement):
    """
    Wrapper for package template
    """
    template = "rate/package.xml"
    
    def __init__(self, weight, packaging_type_code=None, dimensions=None, options=None, large=False):
        """
        @param weight: weight of the package in pounds
        @param packaging_type: a packaging type code
        @param dimensions: package dimensions as a dictionary with keys width, height, and length
        @param options: extra package options (see UPS API docs)
        @param large: boolean flag indicating whether this package is oversized
        """
        self.weight = weight
        self.packaging_type_code = packaging_type_code or '02'
        self.dimensions = dimensions
        self.options = options
        self.large = large
        
    def get_context(self):
        return {'package' : self }
    
        