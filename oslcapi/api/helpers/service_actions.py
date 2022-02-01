import os

from google.cloud import storage
from rdflib import Graph, URIRef, Literal, Namespace, RDF

OSLC = Namespace('http://open-services.net/ns/core#')

# Get GCP Credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
    '/Users/alejandrovargasperez/GCP Credentials/rock-sentinel-333408-7a09dab643b4.json'
base_url = 'http://localhost:5001/GCP_OSLC'


def create_resource(service_provider, graph, store):
    query_bucket = """

        PREFIX dcterms: <http://purl.org/dc/terms/>

        SELECT ?name ?location ?storage_class

        WHERE {
            ?s dcterms:title ?name .
            ?s dcterms:spatial ?location .
            ?s dcterms:source ?storage_class .
        }
    """

    query_type = """

                    PREFIX on: <http://localhost:5001/GCP_OSLC/>

                    SELECT ?type

                    WHERE {
                        ?s rdf:type ?type .
                    }

                """

    # Check Service Provider
    provider_type = None
    for r in service_provider.rdf.query(query_type):
        if r["type"] == URIRef(base_url + '/FilesystemService'):
            provider_type = 'Cloud Storage'
        elif r["type"] == URIRef(base_url + '/VirtualMachineService'):
            provider_type = 'Compute Engine'
        elif r["type"] == URIRef(base_url + '/ContainerService'):
            provider_type = 'Kubernetes Engine'


    '''
    
        CLOUD STORAGE RESOURCE CREATION
    
    '''

    if provider_type == 'Cloud Storage':
        for name, location, storage_class in graph.query(query_bucket):

            # It would be better if we check the bucket properties defined on BucketResourceShape
            storage_client = storage.Client()

            bucket = storage_client.bucket(name)
            bucket.storage_class = storage_class
            new_bucket = storage_client.create_bucket(bucket, location=location)

            resource = store.add_resource(service_provider, new_bucket)

        for p, o in graph.predicate_objects(None):
            resource.rdf.add((resource.uri, p, o))

        return new_bucket



def update_resource(service_provider, resource, graph, store):
    query_type = """

                        PREFIX on: <http://localhost:5001/GCP_OSLC/>

                        SELECT ?type

                        WHERE {
                            ?s rdf:type ?type .
                        }

                    """

    # Check Service Provider
    provider_type = None
    for r in service_provider.rdf.query(query_type):
        if r["type"] == URIRef(base_url + '/FilesystemService'):
            provider_type = 'Cloud Storage'
        elif r["type"] == URIRef(base_url + '/VirtualMachineService'):
            provider_type = 'Compute Engine'
        elif r["type"] == URIRef(base_url + '/ContainerService'):
            provider_type = 'Kubernetes Engine'

    '''

        CLOUD STORAGE RESOURCE UPDATE
        
    '''

    if provider_type == 'Cloud Storage':
        print('Cloud Storage bucket cannot be modified!')



def delete_resource(uri):
    g = Graph()
    g.add((URIRef(uri), RDF.type, OSLC.serviceProvider))
    g.add((URIRef(uri), RDF.comment, Literal("Deleted")))

    # Call service api to delete a resource
    # store.generate_change_event(URIRef(uri), 'Deletion')

    return g