import logging, time

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from oslcapi.api.helpers.service_api import *

PROJECT_ID = 'weighty-time-341718'

OSLC = Namespace('http://open-services.net/ns/core#')
base_url = 'http://localhost:5001/GCP_OSLC/'

log = logging.getLogger('tester.sub')


def create_resource(service_provider, graph, store):
    query_bucket = """

        PREFIX gcp: <http://localhost:5001/GCP_OSLC/>

        SELECT ?name ?location ?storage_class

        WHERE {
            ?s gcp:directoryName ?name .
            ?s gcp:directoryLocation ?location .
            ?s gcp:directoryStorageClass ?storage_class .
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
            for name, location, storage_class in graph.query(query_bucket):
                # It would be better if we check the bucket properties defined on BucketResourceShape
                storage_client = storage.Client()

                bucket = storage_client.bucket(name)
                bucket.storage_class = str(storage_class)
                new_bucket = storage_client.create_bucket(bucket, location=location)

                # Add resource to the store
                resource = store.add_resource(service_provider, new_bucket)

            for p, o in graph.predicate_objects(None):
                resource.rdf.add((resource.uri, p, o))

        case 'VirtualMachineService':
            for instance_name, zone in graph.query(query_instance):
                instance = create_instance(PROJECT_ID, zone, instance_name)
                new_instance = get_instance(PROJECT_ID, instance.name, zone)
                # Add resource to the store
                resource = store.add_resource(service_provider, new_instance)
            for p, o in graph.predicate_objects(None):
                resource.rdf.add((resource.uri, p, o))
    return resource.rdf


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


def delete_resource(service_provider, graph, store):
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

    g = Graph()

    match service_provider.module.description:
        case 'FilesystemService':
            for name in graph.query(query_bucket):
                bucket_name = str(name.asdict()['name'].toPython())

                storage_client = storage.Client()

                bucket = storage_client.get_bucket(bucket_name)
                bucket.delete()
                log.warning('Bucket {} deleted succesfully!'.format(bucket.id))

                for oslc_resource in service_provider.oslc_resources:
                    if oslc_resource.element.id == str(bucket.id):
                        oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
                        #store.generate_change_event(URIRef(oslc_resource.uri), 'Deletion')
                        g.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
                        return g

        case 'VirtualMachineService':
            for name, zone in graph.query(query_instance):
                instance_client = compute_v1.InstancesClient()
                operation_client = compute_v1.ZoneOperationsClient()
                deleted_instance = get_instance(PROJECT_ID, name, zone)

                print(f"Deleting {name} from {zone}...")
                operation = instance_client.delete_unary(
                    project=PROJECT_ID, zone=zone, instance=name
                )
                start = time.time()
                while operation.status != compute_v1.Operation.Status.DONE:
                    operation = operation_client.wait(
                        operation=operation.name, zone=zone, project=PROJECT_ID
                    )
                    if time.time() - start >= 300:  # 5 minutes
                        raise TimeoutError()
                if operation.error:
                    print("Error during deletion:", operation.error, file=sys.stderr)
                    return
                if operation.warnings:
                    print("Warning during deletion:", operation.warnings, file=sys.stderr)
                print(f"Instance {name} deleted.")

                for oslc_resource in service_provider.oslc_resources:
                    if oslc_resource.element.id == str(deleted_instance.name):
                        oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
                        #store.generate_change_event(URIRef(oslc_resource.uri), 'Deletion')
                        g.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
                        return g
