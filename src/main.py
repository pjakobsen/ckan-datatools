#!/usr/bin/python

import sys, getopt
from optparse import OptionParser
import setup_data
import urllib2
import json
from pprint import pprint 

class Package:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'package' field values, including extras  '''
    pass
class Resourse:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'resource' field values, including extras  '''
    pass

class DataImport:
    protocol = 'http://'
    def __init__(self,top_domain):
        self.top_domain = top_domain
        self.api_base = "/api/action/"
        self.port = 5000
        self.debug_proxy = 'http://localhost:8888'
        self.url =  self.protocol + self.top_domain + self.api_base
        pass
    def test(self):
        ''' Creates a test package in CKAN, retrieves it to verify that it was entered, and then deletes it '''
        test_package = {'name':'delete-me-package','title':'Test Package Title'}
        response = self.api3_call('package_create',test_package)
        print response
        #this is a bit confusing: you can pass the 'name' to 'id' to delete the package
        delete_package = {'id':'delete-me-package'}
        response = self.api3_call('package_delete',delete_package)
        print response
        
    def list_by_owner(self,owner):
        response = self.api3_call('pacckage_list',{})
        for item in response:
            print item['name']
    
    def purge_by_owner(self,owner):
        #package_list -d '{}'
        pass
   
    def pre_populate(self):
        ''' delegation method  '''
        self.create_organizations()
   
    def create_organizations(self):
        ''' Create Government Organizations in CKAN '''
        print "creating organizations for " + self.top_domain
        for d in setup_data.departments:
            organization = {'name':d['name'],'title':d['title'], 'description':d['description']}
            self.api3_call('organization_create',organization)
    
    def api3_call(self,call,payload): 
       ''' To use a proxy for debugging JSON,  set it here  '''
       proxy_handler = urllib2.ProxyHandler({'http': self.debug_proxy})
       #An undocument trick is to create an empty proxy handler to force urllib2 not to use a proxy
       #proxy_handler = urllib2.ProxyHandler({})
       opener = urllib2.build_opener(proxy_handler)
       url = self.url+call 
       print url
       header = {'Authorization':'tester','Content-Type': 'application/json'}
       data=json.dumps(payload)
       print data
       req = urllib2.Request(url, data, header)
       try:
           r = opener.open(req)
           result = json.loads(r.read())
           if result['success']: 
               return result
           elif result['false']:
               print "*******  API ERROR  ********"
               print result
               
       except urllib2.HTTPError as h:
           print "some Error "
           print h

            
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser('Command line interface for GoC Open Data import tools.')
    parser.add_argument("--server", nargs="?", help="server, eg localhost:5000")
    parser.add_argument("p", help="proxy, eg for debugging etc.")
    parser.add_argument("c", help="command [ list | load | purge ]")
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                   const=sum, default=max,
                   help='sum the integers (default: find the max)')
    args = parser.parse_args()
    