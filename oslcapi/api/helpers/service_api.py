from rdflib import Literal, Namespace, DCTERMS

import typing
from google.cloud import storage
import google.cloud.compute_v1 as compute_v1
from google.cloud.compute_v1 import Instance
from google.cloud.storage import Bucket

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


'''

    COMPUTE ENGINE FUNCTIONS

'''


# Get a list of active VMs
def list_instances(
    project_id: str,
) -> typing.Dict[str, typing.Iterable[compute_v1.Instance]]:
    instance_client = compute_v1.InstancesClient()
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    request = compute_v1.AggregatedListInstancesRequest(
        project=project_id, max_results=5
    )
    agg_list = instance_client.aggregated_list(request=request)
    all_instances = {}
    for zone, response in agg_list:
        if response.instances:
            all_instances[zone] = response.instances
    return all_instances

# Module -> ServiceProvider
def module_to_service_provider(module, service_provider):
    service_provider.rdf.add((service_provider.uri, DCTERMS.identifier, Literal(module.id)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.title, Literal(module.title)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.description, Literal(module.description)))


# Resource -> OSLC Resource
def directory_to_oslc_resource(element, resource):
    if isinstance(element, Bucket):
        resource.rdf.add((resource.uri, DCTERMS.identifier, Literal(element.id)))
        resource.rdf.add((resource.uri, DCTERMS.title, Literal(element.name)))
        resource.rdf.add((resource.uri, DCTERMS.spatial, Literal(element.location)))
        resource.rdf.add((resource.uri, DCTERMS.created, Literal(element.time_created)))
        resource.rdf.add((resource.uri, OSLC.details, Literal(element.self_link)))
    if isinstance(element, Instance):
        resource.rdf.add((resource.uri, DCTERMS.identifier, Literal(element.name)))
        resource.rdf.add((resource.uri, DCTERMS.spatial, Literal(element.zone)))
        resource.rdf.add((resource.uri, DCTERMS.created, Literal(element.creation_timestamp)))
        resource.rdf.add((resource.uri, OSLC.details, Literal(element.status)))
