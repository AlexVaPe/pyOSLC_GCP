from rdflib import Literal, Namespace, DCTERMS

import typing
from google.cloud import storage
import google.cloud.compute_v1 as compute_v1
from google.cloud.compute_v1 import Instance
from google.cloud.storage import Bucket
import googleapiclient.discovery

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')

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

'''

    KUBERNETES ENGINE FUNCTIONS

'''

def list_clusters(project_id):
    """Lists all clusters and associated node pools."""
    service = googleapiclient.discovery.build('container', 'v1')
    clusters_resource = service.projects().zones().clusters()
    # All zones
    zone = '-'

    return clusters_resource.list(projectId=project_id, zone=zone).execute()

'''

    RESOURCE -> OLSC MAPPING

'''

# Module -> ServiceProvider
def module_to_service_provider(module, service_provider):
    match module.description:
        case "FilesystemService":
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.filesystemServiceId, Literal(module.id)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.filesystemServiceTitle,
                                      Literal(module.title)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.filesystemServiceDescription,
                                      Literal(module.description)))
        case "VirtualMachineService":
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.virtualMachineServiceId, Literal(module.id)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.virtualMachineServiceTitle,
                                      Literal(module.title)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.virtualMachineServiceDescription,
                                      Literal(module.description)))
        case "ContainerService":
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.containerServiceId,
                                      Literal(module.id)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.containerServiceTitle,
                                      Literal(module.title)))
            service_provider.rdf.add((service_provider.uri, OSLC_CloudProvider.containerServiceDescription,
                                      Literal(module.description)))

# Resource -> OSLC Resource
def directory_to_oslc_resource(element, resource):
    if isinstance(element, Bucket):
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryId, Literal(element.id)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryName, Literal(element.name)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryLocation, Literal(element.location)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.timeCreated, Literal(element.time_created)))
        resource.rdf.add((resource.uri, OSLC.details, Literal(element.self_link)))
    if isinstance(element, Instance):
        resource.rdf.add((resource.uri, OSLC_CloudProvider.instanceName, Literal(element.name)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.instanceZone, Literal(element.zone)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.instanceCreationTimestamp,
                          Literal(element.creation_timestamp)))
        resource.rdf.add((resource.uri, OSLC.details, Literal(element.status)))
    if isinstance(element, dict):
        resource.rdf.add((resource.uri, OSLC_CloudProvider.clusterName, Literal(element['name'])))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.clusterStatus, Literal(element['status'])))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.clusterMasterVersion,
                          Literal(element['currentMasterVersion'])))
        resource.rdf.add((resource.uri, OSLC.details, Literal(element['status'])))