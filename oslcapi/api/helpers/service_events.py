import os

import logging, requests
from rdflib import Namespace, Literal, Graph
from rdflib.namespace import DCTERMS, RDF, RDFS
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID as default

from oslcapi.api.helpers.service_api import get_bucket

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_EVENT = Namespace('http://open-services.net/ns/events#')

# Connect to fuseki triplestore.
FUSEKI_USER = os.getenv("FUSEKI_USER")
FUSEKI_PWD = os.getenv("FUSEKI_PWD")
fuseki_store = SPARQLUpdateStore(auth=(FUSEKI_USER,FUSEKI_PWD))
query_endpoint = 'http://fuseki.demos.gsi.upm.es/oslc-gc2/query'
update_endpoint = 'http://fuseki.demos.gsi.upm.es/oslc-gc2/update'
fuseki_data_endpoint = 'http://fuseki.demos.gsi.upm.es/oslc-gc2/data'
fuseki_store.open((query_endpoint, update_endpoint))


def generate_creation_event(resource, store):
    log.warning('Creation event generated')

    store.trs.generate_change_event(resource, 'Creation')

    # Generate OSLC Event Resource for Fuseki Endpoint
    g = Graph(fuseki_store, identifier=default)
    g.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g.add((resource.uri, DCTERMS.description, Literal('Creation Event')))

    # Generate OSLC Event Resource for Kafka Topic
    g2 = Graph()
    g2.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g2.add((resource.uri, DCTERMS.description, Literal('Creation Event')))

    return g2


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

    # Generate OSLC Event Resource for Fuseki Endpoint
    g = Graph(fuseki_store, identifier=default)
    g.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g.add((resource.uri, DCTERMS.description, Literal('Deletion Event')))

    # Generate OSLC Event Resource for Kafka Topic
    g2 = Graph()
    g2.add((resource.uri, RDF.type, OSLC_EVENT.Event))
    g2.add((resource.uri, DCTERMS.description, Literal('Deletion Event')))

    return g2
