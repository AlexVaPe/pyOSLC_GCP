from rdflib import Graph, Literal, Namespace, DCTERMS, RDF
from google.cloud import storage
import os

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

# Get GCP Credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
    '/Users/alejandrovargasperez/GCP Credentials/rock-sentinel-333408-7a09dab643b4.json'

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


def bucket_to_service_provider(bucket, service_provider):
    service_provider.rdf.add((service_provider.uri, DCTERMS.identifier, Literal(bucket.id)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.title, Literal(bucket.name)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.location, Literal(bucket.location)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.created, Literal(bucket.time_created)))
    service_provider.rdf.add((service_provider.uri, OSLC.details, Literal(bucket.self_link)))

# To be modified
def element_to_oslc_resource(element, resource):
    resource.rdf.add((resource.uri, DCTERMS.identifier, Literal(element.number)))
    resource.rdf.add((resource.uri, DCTERMS.title, Literal(element.title, datatype=RDF.XMLLiteral)))
    resource.rdf.add((resource.uri, DCTERMS.description, Literal(element.body)))
    resource.rdf.add((resource.uri, DCTERMS.created, Literal(element.created_at)))
    resource.rdf.add((resource.uri, DCTERMS.modified, Literal(element.updated_at)))
    resource.rdf.add((resource.uri, DCTERMS.contributor, Literal(element.user.name)))
    # to be modified
    resource.rdf.add((resource.uri, OSLC_CM.status, Literal(element.state)))
