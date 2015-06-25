"""
Base implementation of UPS API service
"""
from StringIO import StringIO
import string
import urllib2
from urllib2 import Request
from ups.utils import xmltodict
from ups.errors import UPSXMLError

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
    
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('ups'), extensions=['jinja2.ext.with_'])

UPS_CONNECTION_URL = "https://onlinetools.ups.com/ups.app/xml/"
UPS_CONNECTION_TEST = "https://wwwcie.ups.com/ups.app/xml/"

class UPSConnection(object):
    """
    Represents a connection to the UPS API server, given a
    UPSRequest instance, can query the UPS API.
    """    
    def __init__(self, user_id, password, access_key, url=None):
        self.url = url or UPS_CONNECTION_URL
        self.user_id = user_id
        self.password = password
        self.access_key = access_key
    
    def submit_xml(self, xml, url):
        """
        Submit the request xml to the API server
        
        @param xml: a string representation of a UPS Request XML document
        @return: an Element instance wrapping the response from UPS
        """
        request = Request(url, xml)
        request.add_header("Method", "POST")
        request.add_header("Connection", "Keep-Alive")
        request.add_header("Content-Type", "text/xml; charset=utf-8")
        
        response = urllib2.urlopen(request)
        root = ET.parse(response).getroot()
        
        return root
        
    def parse_xml(self, xml):
        """
        Parse an XML response to a Python dictionary
        
        @throws: UPSXMLError on error
        @param xml: an XML element
        @return: a dictionary representing the XML response
        """
        error = xml.find('.//Error')
        if error:
            raise UPSXMLError(error)
        
        return xmltodict(xml)
    
    def make_xml(self, request):
        """
        Build the request xml document (actually two documents)
        
        @param request: a UPSRequest subclass
        @return: tuple of xml document, and url to post it to
        """
        auth_xml = self._make_auth_xml()
        data_xml = request.render()
        request_url = string.join((self.url, request.API),"")
          
        xml = string.join((auth_xml,data_xml), "\n")
        
        return xml, request_url
        
    def _make_auth_xml(self):
        """
        Build the UPS AccessRequest xml document
        
        @return string: the AccessRequest document
        """
        security = UPSSecurityElement(self.user_id, self.password, self.access_key)
        return security.render()
    
    
    def execute(self,request):
        """
        build and send a UPS api call
        
        @param data: a dictionary of request data
        @return: a dictionary represenation of the API response
        """
        xml, request_url = self.make_xml(request)            
        return self.parse_xml(self.submit_xml(xml, request_url))
 
class UPSElement(object):   
    """
    Base class for UPS XML template wrapper
    """    
    template = ""
    
    def render(self):
        """
        render this element to a string using its template
        """
        template = env.get_template(self.template)
        return template.render(self.get_context())
    
    def get_context(self):
        """
        get the context dictionary to be passed to 
        this element's template in self.render()
        
        @return: dict
        """
        return {'obj':self}
    
class UPSSecurityElement(UPSElement):
    """
    Wrapper for UPS AccessRequest element
    """
    template = "common/ups_security.xml"
    
    def __init__(self, user_id, password, access_key):
        """
        """
        self.user_id = user_id
        self.password = password
        self.access_key = access_key
        
    def get_context(self):
        """
        Return a context dictionary for the security element
        
        @return: dictionary
        """
        return {'access_key':self.access_key, 'user_id': self.user_id, 'password': self.password}

class UPSRequest(UPSElement):
    ACTION = ""    
    OPTION = ""
    
    @property
    def API(self):
        return self.ACTION
        
    def get_context(self):
        """
        build the context dictionary to render this request
        """
        return {'request':self}


