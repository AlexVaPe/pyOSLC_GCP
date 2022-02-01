# from owlready2 import *
import logging

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF

from oslcapi.api.helpers import module_to_service_provider, directory_to_oslc_resource, list_buckets

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')

# Import GCP Semantic Model
path_to_owl = "/Users/alejandrovargasperez/Documents/UPM/MUIT/TFM/gcp-oslc_adapter/Semantic model/GoogleCloud_OSLC.owl"
# onto = get_ontology("file://" + path_to_owl).load()
# Load the owl into a Graph
# rdf = default_world.as_rdflib_graph()
rdf = Graph()
rdf.parse("file://" + path_to_owl, format='xml')

base_url = 'http://localhost:5001/GCP_OSLC'


class OSLCStore:
    def __init__(self, trs):
        self.catalog = ServiceProviderCatalog()
        self.initialize_oslc()

        self.trs = trs
        self.trs.initialize_trs(self.catalog)

    def initialize_oslc(self):
        # Filesystem Service Provider
        cloudStorage = FilesystemService('CloudStorage', 'Google Cloud Storage',
                                         'Filesystem Service of Google Cloud')
        filesystem_service_provider = ServiceProvider(cloudStorage, len(self.catalog.service_providers) + 1)
        self.catalog.add(filesystem_service_provider)

        for directory in list_buckets():
            self.add_resource(filesystem_service_provider, directory)

        log.warning('OSLC store loaded')

    def add_resource(self, service_provider, element):
        resource = OSLCResource(service_provider, element, len(service_provider.oslc_resources) + 1)
        service_provider.oslc_resources.append(resource)
        return resource

    def replace_resource(self, service_provider, element, resource):
        index = service_provider.oslc_resources.index(resource)
        updated_resource = OSLCResource(service_provider, element, resource.id)
        service_provider.oslc_resources.remove(resource)
        service_provider.oslc_resources.insert(index, updated_resource)
        return updated_resource


'''

    DEFINITION OF SERVICE PROVIDER CATALOG

'''


class ServiceProviderCatalog:
    def __init__(self):
        self.uri = URIRef(base_url + '/service/serviceProviders/catalog')

        self.service_providers = []

        # Google Cloud Platform Catalog
        rdf.add((self.uri, DCTERMS.title, Literal('Google Cloud Catalog')))
        rdf.add((self.uri, DCTERMS.description, Literal('Google Cloud Platform Catalog')))
        rdf.add((self.uri, RDF.type, OSLC.ServiceProviderCatalog))

    def add(self, service_provider):
        rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        self.service_providers.append(service_provider)


'''

    DEFINITION OF SERVICE PROVIDER

'''


class ServiceProvider:
    def __init__(self, module, id):
        self.rdf = rdf
        self.id = id
        self.uri = URIRef(base_url + '/service/serviceProviders/' + str(self.id))
        self.module = module

        self.oslc_resources = []

        rdf.add((self.uri, RDF.type, OSLC.ServiceProvider))

        if module.id == 'CloudStorage':
            service = BNode()

            rdf.add((self.uri, OSLC.service, service))
            rdf.add((service, RDF.type, OSLC.Service))
            # rdf.add((service, OSLC.domain, URIRef('http://open-services.net/ns/am#')))

            creationFactory = BNode()

            rdf.add((service, OSLC.creationFactory, creationFactory))
            rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
            rdf.add((creationFactory, OSLC.resourceType, OSLC_CloudProvider.Directory))
            rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))

            rdf.add((creationFactory, OSLC.creation,
                     URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/directory')))

            queryCapability = BNode()

            rdf.add((service, OSLC.queryCapability, queryCapability))
            rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
            rdf.add((queryCapability, OSLC.resourceType, OSLC_CloudProvider.Directory))
            rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
            rdf.add((queryCapability, OSLC.queryBase,
                     URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/directory')))

            module_to_service_provider(module, self)


class FilesystemService:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


'''

    DEFINITION OF OLSC RESOURCE

'''


class OSLCResource:
    def __init__(self, service_provider, element, id):
        self.rdf = rdf
        self.id = id
        self.uri = URIRef(
            base_url + '/service/serviceProviders/' + str(service_provider) + '/oslc/resource/' + str(element))

        if service_provider.module.id == 'CloudStorage':
            rdf.add((self.uri, RDF.type, OSLC_CloudProvider.Directory))
        rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        directory_to_oslc_resource(element, self)
