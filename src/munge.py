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

class DataManager:
    protocol = 'http://'
    def __init__(self, server):
        self.server = 'http://' + server
        self.api_base = "/api/action/"
        self.port = 5000
        self.debug_proxy = 'http://localhost:8888'
        self.url =  self.server + self.api_base
        pass
    def test(self):
        ''' Creates a test package in CKAN, retrieves it to verify that it was entered, and then deletes it '''
        test_package = {'name':'delete-me-package','title':'Test Package Title'}
        response = self.api3_call('package_create',test_package)

        #this is a bit confusing: you can pass the 'name' to 'id' to delete the package
        delete_package = {'id':'delete-me-package'}
        response = self.api3_call('package_delete',delete_package)
       
    def _packages(self,org): 
        packs = [] 
        if org != 'all':
            response = self.api3_call('package_search',{'q': u'groups: "'+ org + '"'}) 
            for item in response['result']['results']:
                packs.append(item['name'])
        else:
            response = self.api3_call('package_list',{}) 
            for item in response['result']:
                packs.append(item)   
        return packs
                
    def list_by_organization(self,org):
        for item in self._packages(org):
            print item

    def delete_by_owner(self,org):
      for item in self._packages(org):
            self.api3_call('package_delete', {'id':item})

    
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
       header = {'Authorization':'tester','Content-Type': 'application/json'}
       data=json.dumps(payload)
      
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
    parser = argparse.ArgumentParser('munge.py')
    subparsers = parser.add_subparsers(help='commands')
    
    # Commands for reporting on existing data
    report_parser = subparsers.add_parser('ckan', help='List Dataset Summary')
    report_parser.add_argument('action', action='store', help='Data entity type', choices=['list','delete'])
    report_parser.add_argument('entity', action='store', help='Data entity type', choices=['pack','org','user'])
    report_parser.add_argument('organization', action='store', help='Organization',default='all')

    # Commands for creating new data
    create_parser = subparsers.add_parser('make', help='Create New Data')
    create_parser.add_argument('dirname', action='store', help='New directory to create')
    create_parser.add_argument('--read-only', default=False, action='store_true',
                           help='Set permissions to prevent writing to the directory',
                           )
    
   
    parser.add_argument("-o", help="Perform and operation on data")

    parser.add_argument("-s","--server", help="CKAN Server.  Default is localhost:5000", default="localhost:5000")
    parser.add_argument("-p","--proxy", help="Proxy for debugging etc. Default is None")
    parser.add_argument("-v", "--verbose", help="increase output verbosity")
 
    args = parser.parse_args()



    if args.action == 'list':
        DataManager(args.server).list_by_organization(args.organization)
    elif args.action == 'delete':
        DataManager(args.server).delete_by_owner(args.organization)
        
   