import os

from google.cloud import storage
from rdflib import Literal, Namespace, DCTERMS

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

'''

    CLOUD STORAGE FUNCTIONS

'''


# Get a list of Google Cloud Storage Buckets
def list_buckets():
    storage_client = storage.Client()
    return storage_client.list_buckets()


# Get metadata of a specific bucket
def get_bucket(bucket_name):
    storage_client = storage.Client()
    return storage_client.get_bucket(bucket_name)

# Module -> ServiceProvider
def module_to_service_provider(module, service_provider):
    service_provider.rdf.add((service_provider.uri, DCTERMS.identifier, Literal(module.id)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.title, Literal(module.title)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.description, Literal(module.description)))


# Resource -> OSLC Resource
def directory_to_oslc_resource(element, resource):
    resource.rdf.add((resource.uri, DCTERMS.identifier, Literal(element.id)))
    resource.rdf.add((resource.uri, DCTERMS.title, Literal(element.name)))
    resource.rdf.add((resource.uri, DCTERMS.spatial, Literal(element.location)))
    resource.rdf.add((resource.uri, DCTERMS.created, Literal(element.time_created)))
    resource.rdf.add((resource.uri, OSLC.details, Literal(element.self_link)))
