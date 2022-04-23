import logging

from oslcapi.api.helpers.service_api import *

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
PROJECT_ID = 'weighty-time-341718'


def generate_creation_event(graph, store, service_provider):
    log.warning('Creation event generated')

    query_bucket = """

        PREFIX gcp: <http://localhost:5001/GCP_OSLC/>

        SELECT ?name

        WHERE {
            ?s gcp:directoryName ?name .
        }
    """

    query_instance = """

            PREFIX gcp: <http://localhost:5001/GCP_OSLC/>

            SELECT ?name ?zone

            WHERE {
                ?s gcp:instanceName ?name .
                ?s gcp:instanceZone ?zone .
            }
        """

    match service_provider.module.description:
        case 'FilesystemService':
            for name in graph.query(query_bucket):
                bucket = get_bucket(name)
                service_provider = next(service_provider for service_provider in store.catalog.service_providers if
                                        Literal(bucket.id) in service_provider.rdf.objects(None, DCTERMS.identifier))
                resource = store.add_resource(service_provider, bucket)
                store.trs.generate_change_event(resource, 'Creation')

        case 'VirtualMachineService':
            for instance_name, zone in graph.query(query_instance):
                instance = get_instance(PROJECT_ID, instance_name, zone)
                resource = store.add_resource(service_provider, instance)
                store.trs.generate_change_event(resource, 'Creation')
    return


def generate_modification_event(payload, store):
    log.warning('Modification event generated')

    bucket = get_bucket(payload['bucket'])

    service_provider = next(service_provider for service_provider in store.catalog.service_providers if
                            Literal(bucket.id) in service_provider.rdf.objects(None, DCTERMS.identifier))
    resource = next(resource for resource in service_provider.oslc_resources if
                    Literal(bucket.number) in resource.rdf.objects(None, DCTERMS.identifier))

    service_provider.oslc_resources.remove(resource)

    resource = store.add_resource(service_provider, bucket)
    store.trs.generate_change_event(resource, 'Modification')

    return


def generate_deletion_event(payload, store):
    log.warning('Deletion event generated')
    log.warning(payload)

    return
