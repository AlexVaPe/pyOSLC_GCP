import logging
import os
from rdflib import Namespace, Literal
from rdflib.namespace import DCTERMS

from oslcapi.api.helpers.service_api import get_bucket

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')

# Get GCP Credentials
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/code/oslcapi/rock-sentinel-333408-7a09dab643b4.json'

def generate_creation_event(payload, store):
    log.warning('Creation event generated')

    bucket = get_bucket(payload['bucket'])

    service_provider = next(service_provider for service_provider in store.catalog.service_providers if
                            Literal(bucket.id) in service_provider.rdf.objects(None, DCTERMS.identifier))

    resource = store.add_resource(service_provider, bucket)
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