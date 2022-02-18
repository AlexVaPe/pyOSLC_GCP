import logging
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF

from oslcapi.api.helpers import module_to_service_provider, directory_to_oslc_resource, list_buckets

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')

# Import GCP Semantic Model
my_rdf = Graph()
my_rdf.parse("https://raw.githubusercontent.com/AlexVaPe/pyOSLC_GCP/main/Semantic_model/GoogleCloud_OSLC.owl", format='xml')

base_url = 'http://localhost:5001/'


class OSLCStore:
    def __init__(self, trs):
        self.catalog = ServiceProviderCatalog(my_rdf)
        self.initialize_oslc()

        self.trs = trs
        self.trs.initialize_trs(self.catalog)

    def initialize_oslc(self):
        # Filesystem Service Provider
        cloudStorage = FilesystemService('CloudStorage', 'Google Cloud Storage',
                                         'Filesystem Service of Google Cloud')
        filesystem_service_provider = ServiceProvider(cloudStorage, len(self.catalog.service_providers) + 1, my_rdf)
        self.catalog.add(filesystem_service_provider)

        for directory in list_buckets():
            self.add_resource(filesystem_service_provider, directory)

        log.warning('OSLC store loaded')

    def add_resource(self, service_provider, element):
        resource = OSLCResource(service_provider, element, len(service_provider.oslc_resources) + 1, my_rdf)
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
    def __init__(self, my_rdf):
        self.uri = URIRef(base_url + '/service/serviceProviders/catalog')
        self.service_providers = []
        self.rdf = Graph()

        # Google Cloud Platform Catalog
        self.rdf.add((self.uri, DCTERMS.title, Literal('Google Cloud Catalog')))
        self.rdf.add((self.uri, DCTERMS.description, Literal('Google Cloud Platform Catalog')))
        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProviderCatalog))
        my_rdf += self.rdf.triples((None, None, None))

        #self.rdf = rdf.triples((None, RDF.type, OSLC.ServiceProviderCatalog))

    def add(self, service_provider):
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        self.service_providers.append(service_provider)


'''

    DEFINITION OF SERVICE PROVIDER

'''


class ServiceProvider:
    def __init__(self, module, id, imported_rdf):
        self.rdf = Graph()
        self.id = id
        self.uri = URIRef(base_url + '/service/serviceProviders/' + str(self.id))
        self.module = module

        self.oslc_resources = []

        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProvider))

        match module.id:
            case "CloudStorage":
                service = BNode()

                self.rdf.add((self.uri, OSLC.service, service))
                self.rdf.add((service, RDF.type, OSLC.Service))
                # rdf.add((service, OSLC.domain, URIRef('http://open-services.net/ns/am#')))

                creationFactory = BNode()

                self.rdf.add((service, OSLC.creationFactory, creationFactory))
                self.rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
                self.rdf.add((creationFactory, OSLC.resourceType, OSLC_CloudProvider.Directory))
                self.rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))

                self.rdf.add((creationFactory, OSLC.creation,
                         URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/directory')))

                queryCapability = BNode()

                self.rdf.add((service, OSLC.queryCapability, queryCapability))
                self.rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
                self.rdf.add((queryCapability, OSLC.resourceType, OSLC_CloudProvider.Directory))
                self.rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
                self.rdf.add((queryCapability, OSLC.queryBase,
                         URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/directory')))
                imported_rdf += self.rdf.triples((None, None, None))

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
    def __init__(self, service_provider, element, id, imported_rdf):
        self.rdf = Graph()
        self.id = id

        match service_provider.module.id:
            case 'CloudStorage':
                self.uri = URIRef(
                    base_url + '/service/serviceProviders/' + str(service_provider.module.id) + '/Directory/'
                    + str(element.id))
                self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.Directory))
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        imported_rdf += self.rdf.triples((None, None, None))

        directory_to_oslc_resource(element, self)
