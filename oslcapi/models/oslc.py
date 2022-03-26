import logging
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF, RDFS
import threading
import time

from oslcapi.api.helpers import module_to_service_provider, directory_to_oslc_resource, list_buckets, list_instances,\
    list_clusters

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')
OSLC_ACTION = Namespace('http://open-services.net/ns/actions#')

# Import GCP Semantic Model
my_rdf = Graph()
my_rdf.parse("https://raw.githubusercontent.com/AlexVaPe/pyOSLC_GCP/main/Semantic_model/GoogleCloud_OSLC.owl",
             format='xml')

base_url = 'http://localhost:5001/GCP_OSLC'

# Google Cloud Project ID
PROJECT_ID = "weighty-time-341718"

class OSLCStore:
    def __init__(self, trs):
        self.rdf = my_rdf
        self.catalog = ServiceProviderCatalog(self.rdf)
        self.initialize_oslc()

        self.trs = trs
        self.trs.initialize_trs(self.catalog)

    def initialize_oslc(self):
        '''

        Data Storage Service - Filesystem Service Provider

        '''

        cloudStorage = FilesystemService('CloudStorage', 'Google Cloud Storage',
                                         'FilesystemService')
        filesystem_service_provider = ServiceProvider(cloudStorage, len(self.catalog.service_providers) + 1, my_rdf)
        self.catalog.add(filesystem_service_provider)

        for directory in list_buckets():
            self.add_resource(filesystem_service_provider, directory)

        '''
        
        Computation Service - VM Service
        
        '''

        computeEngine = VirtualMachineService('ComputeEngine', 'Google Compute Engine', 'VirtualMachineService')
        vm_service_provider = ServiceProvider(computeEngine, len(self.catalog.service_providers) + 1, my_rdf)
        self.catalog.add(vm_service_provider)
        # We obtain all VM instances
        all_instances = list_instances(PROJECT_ID)

        for zone in list_instances(PROJECT_ID):
            for instance in all_instances[zone]:
                self.add_resource(vm_service_provider, instance)

        '''

        Container Service - Kubernetes Service

        '''

        kubernetesEngine = ContainerService('GoogleCloudKubernetesEngine', 'Google Cloud Kubernetes Engine',
                                            'ContainerService')
        computation_service_provider = ServiceProvider(kubernetesEngine, len(self.catalog.service_providers) + 1, my_rdf)
        self.catalog.add(computation_service_provider)

        # We obtain all clusters
        clusters_response = list_clusters(PROJECT_ID)

        for cluster in clusters_response.get('clusters', []):
            self.add_resource(computation_service_provider, cluster)


        log.warning('OSLC store loaded')

        # We initialize the thread for updating the resources
        '''x = threading.Thread\
            (target=self.update_resources_thread,
             args=(filesystem_service_provider,vm_service_provider, computation_service_provider),
             daemon=True)
        x.start()'''


    def update_resources_thread(self, filesystem_service_provider, vm_service_provider, computation_service_provider):
        while True:
            log.warning('Starting thread...')
            cloud_directory_list = []
            cloud_instance_list = []
            cloud_cluster_list = []
            # Directory update
            for directory in list_buckets():
                cloud_directory_list.append(directory.id)
                self.add_resource(filesystem_service_provider, directory)
            # Check if there is any resource deleted
            for oslc_resource in filesystem_service_provider.oslc_resources:
                if oslc_resource.element.id not in cloud_directory_list:
                    oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
            # Instance update
            # We obtain all VM instances
            all_instances = list_instances(PROJECT_ID)
            for zone in list_instances(PROJECT_ID):
                for instance in all_instances[zone]:
                    cloud_instance_list.append(instance.id)
                    self.add_resource(vm_service_provider, instance)
            # Check if there is any resource deleted
            for oslc_resource in vm_service_provider.oslc_resources:
                if oslc_resource.element.id not in cloud_instance_list:
                    oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
            # Cluster update
            # We obtain all clusters
            clusters_response = list_clusters(PROJECT_ID)
            for cluster in clusters_response.get('clusters', []):
                cloud_cluster_list.append(cluster['name'])
                self.add_resource(computation_service_provider, cluster)
            # Check if there is any resource deleted
            for oslc_resource in computation_service_provider.oslc_resources:
                if oslc_resource.element['name'] not in cloud_cluster_list:
                    oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))

            log.warning('Thread finished. Start sleeping...')
            time.sleep(10)

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
        self.oslc_actions = []
        self.rdf = Graph()

        # Google Cloud Platform Catalog
        self.rdf.add((self.uri, DCTERMS.title, Literal('Google Cloud Catalog')))
        self.rdf.add((self.uri, DCTERMS.description, Literal('Google Cloud Platform Catalog')))
        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProviderCatalog))
        my_rdf += self.rdf.triples((None, None, None))

        # self.rdf = rdf.triples((None, RDF.type, OSLC.ServiceProviderCatalog))

    def add(self, service_provider):
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        self.service_providers.append(service_provider)

    def create_action(self, id, service_provider, action_type):
        action = Action(id, service_provider, action_type)
        self.oslc_actions.append(action)
        return action


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

        # Filesystem Service Provider
        if isinstance(module, FilesystemService):
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.FilesystemService))

            service = BNode()

            self.rdf.add((self.uri, OSLC.service, service))
            self.rdf.add((service, RDF.type, OSLC.Service))

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

        # VirtualMachine Service Provider
        if isinstance(module, VirtualMachineService):
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.VirtualMachineService))

            service = BNode()

            self.rdf.add((self.uri, OSLC.service, service))
            self.rdf.add((service, RDF.type, OSLC.Service))

            creationFactory = BNode()

            self.rdf.add((service, OSLC.creationFactory, creationFactory))
            self.rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
            self.rdf.add((creationFactory, OSLC.resourceType, OSLC_CloudProvider.Instance))
            self.rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))

            self.rdf.add((creationFactory, OSLC.creation,
                          URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/instance')))

            queryCapability = BNode()

            self.rdf.add((service, OSLC.queryCapability, queryCapability))
            self.rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
            self.rdf.add((queryCapability, OSLC.resourceType, OSLC_CloudProvider.Instance))
            self.rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
            self.rdf.add((queryCapability, OSLC.queryBase,
                          URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/instance')))
            imported_rdf += self.rdf.triples((None, None, None))

            module_to_service_provider(module, self)

        # Container Service Provider
        if isinstance(module, ContainerService):
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.ContainerService))

            service = BNode()

            self.rdf.add((self.uri, OSLC.service, service))
            self.rdf.add((service, RDF.type, OSLC.Service))

            creationFactory = BNode()

            self.rdf.add((service, OSLC.creationFactory, creationFactory))
            self.rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
            self.rdf.add((creationFactory, OSLC.resourceType, OSLC_CloudProvider.Cluster))
            self.rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))

            self.rdf.add((creationFactory, OSLC.creation,
                          URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/cluster')))

            queryCapability = BNode()

            self.rdf.add((service, OSLC.queryCapability, queryCapability))
            self.rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
            self.rdf.add((queryCapability, OSLC.resourceType, OSLC_CloudProvider.Cluster))
            self.rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
            self.rdf.add((queryCapability, OSLC.queryBase,
                          URIRef(base_url + '/service/serviceProviders/' + str(self.id) + '/cluster')))
            imported_rdf += self.rdf.triples((None, None, None))

            module_to_service_provider(module, self)


class FilesystemService:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


class VirtualMachineService:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

class ContainerService:
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
        self.uri = URIRef(base_url)
        self.element = element

        if isinstance(service_provider.module, FilesystemService):
            self.uri = URIRef(
                base_url + '/service/serviceProviders/' + str(service_provider.module.id) + '/directory/'
                + str(element.id))
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.Directory))
            self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        if isinstance(service_provider.module, VirtualMachineService):
            self.uri = URIRef(
                base_url + '/service/serviceProviders/' + str(service_provider.module.id) + '/instance/'
                + str(element.id))
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.Instance))
            self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        if isinstance(service_provider.module, ContainerService):
            self.uri = URIRef(
                base_url + '/service/serviceProviders/' + str(service_provider.module.id) + '/cluster/'
                + str(element['name']))
            self.rdf.add((self.uri, RDF.type, OSLC_CloudProvider.Cluster))
            self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        imported_rdf += self.rdf.triples((None, None, None))
        directory_to_oslc_resource(element, self)

'''

    DEFINITION OF OSLC ACTIONS

'''

class Action:
    def __init__(self, id, service_provider, action_type):
        self.rdf = Graph()
        self.id = id
        self.service_provider = service_provider
        self.action_type = action_type
        self.uri = URIRef(base_url + '/action/' + str(self.id))

        self.rdf.add((self.uri, RDF.type, OSLC_ACTION.Action))
        self.rdf.add((self.uri, RDF.type, Literal(self.action_type)))
        self.rdf.add((self.uri, OSLC_ACTION.actionProvider, Literal(self.service_provider)))

    def add_result(self, result):
        self.rdf.add((self.uri, OSLC_ACTION.actionResult, Literal(result)))