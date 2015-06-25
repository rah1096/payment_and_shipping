"""
Global errors module for USPS app 
"""
from ups.utils import xmltodict

class UPSXMLError(Exception):
    def __init__(self, element):
        self.info = xmltodict(element)
        super(UPSXMLError, self).__init__("%s Error Code: %s, %s " 
                                          % (self.info['ErrorSeverity'], self.info['ErrorCode'], self.info['ErrorDescription']))