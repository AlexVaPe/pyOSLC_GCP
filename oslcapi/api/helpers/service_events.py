import logging
import os
from rdflib import Namespace, Literal, Graph
from rdflib.namespace import DCTERMS, RDF, RDFS
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID as default

from oslcapi.api.helpers.service_api import get_bucket

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_EVENT = Namespace('http://open-services.net/ns/events#')

# Connect to fuseki triplestore.
store = SPARQLUpdateStore()
query_endpoint = 'https://fuseki.demos.gsi.upm.es/oslc-gc/query'
update_endpoint = 'http://localhost:3030/oslc-gc/update'
store.open((query_endpoint, update_endpoint))


def generate_creation_event(resource, store):
    log.warning('Creation event generated')

    store.trs.generate_change_event(resource, 'Creation')
    # Generate OSLC Event Resource
    g = Graph(store, identifier=default)
    g.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g.add((resource.uri, DCTERMS.description, Literal('Creation Event')))

    return g


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


def generate_deletion_event(resource, store):
    log.warning('Deletion event generated')
    log.warning(resource)
    store.trs.generate_change_event(resource, 'Deletion')
    # Generate OSLC Event Resource
    g = Graph(store, identifier=default)
    g.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g.add((resource.uri, DCTERMS.description, Literal('Deletion Event')))

    return g
