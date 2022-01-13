from oslcapi.api.helpers import get_modules, get_elements, module_to_service_provider, element_to_oslc_resource
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF
import logging

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

base_url = 'http://localhost:5001'


class OSLCStore:
    def __init__(self, trs):
        self.catalog = ServiceProviderCatalog()
        self.initialize_oslc()

        self.trs = trs
        self.trs.initialize_trs(self.catalog)


    def initialize_oslc(self):

        for module in get_modules():
            service_provider = ServiceProvider(module, len(self.catalog.service_providers)+1)
            self.catalog.add(service_provider)

            for element in get_elements(module):
                self.add_resource(service_provider, element)

        log.warning('OSLC store loaded')


    def add_resource(self, service_provider, element):
        resource = OSLCResource(service_provider, element, len(service_provider.oslc_resources)+1)
        service_provider.oslc_resources.append(resource)
        return resource

    def replace_resource(self, service_provider, element, resource):
        index = service_provider.oslc_resources.index(resource)
        updated_resource = OSLCResource(service_provider, element, resource.id)
        service_provider.oslc_resources.remove(resource)
        service_provider.oslc_resources.insert(index, updated_resource)
        return updated_resource

class ServiceProviderCatalog:
    def __init__(self):
        self.rdf = Graph()
        self.uri = URIRef(base_url+'/service/serviceProviders/catalog')

        self.service_providers = []

        self.rdf.add((self.uri, DCTERMS.title, Literal('GitHub OSLC Server')))
        self.rdf.add((self.uri, DCTERMS.description, Literal('A server that provides OSLC capabilities to GitHub')))
        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProviderCatalog))
        self.rdf.add((self.uri, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))

    def add(self, service_provider):
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        self.service_providers.append(service_provider)


class ServiceProvider:
    def __init__(self, module, id):
        self.rdf = Graph()
        self.id = id
        self.uri = URIRef(base_url+'/service/serviceProviders/'+str(self.id))

        self.oslc_resources = []

        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProvider))

        service = BNode()

        self.rdf.add((self.uri, OSLC.service, service))
        self.rdf.add((service, RDF.type, OSLC.Service))
        self.rdf.add((service, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))

        creationFactory = BNode()

        self.rdf.add((service, OSLC.creationFactory, creationFactory))
        self.rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
        self.rdf.add((creationFactory, OSLC.resourceType, OSLC_CM.ChangeRequest))
        self.rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))
        self.rdf.add((creationFactory, OSLC.creation, URIRef(base_url+'/service/serviceProviders/'+str(self.id)+'/changeRequests')))

        queryCapability = BNode()

        self.rdf.add((service, OSLC.queryCapability, queryCapability))
        self.rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
        self.rdf.add((queryCapability, OSLC.resourceType, OSLC_CM.ChangeRequest))
        self.rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
        self.rdf.add((queryCapability, OSLC.queryBase, URIRef(base_url+'/service/serviceProviders/'+str(self.id)+'/changeRequests')))        

        module_to_service_provider(module, self)



class OSLCResource:
    def __init__(self, service_provider, element, id):
        self.rdf = Graph()
        self.id = id
        self.uri = URIRef(base_url+'/service/serviceProviders/'+str(service_provider.id)+'/changeRequests/'+str(self.id))

        self.rdf.add((self.uri, RDF.type, OSLC_CM.ChangeRequest))
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        element_to_oslc_resource(element, self)