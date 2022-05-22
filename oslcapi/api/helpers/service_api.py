from rdflib import Literal, Namespace, DCTERMS

import typing, sys, re
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
    request = compute_v1.AggregatedListInstancesRequest(
        project=project_id, max_results=5
    )
    agg_list = instance_client.aggregated_list(request=request)
    all_instances = {}
    for zone, response in agg_list:
        if response.instances:
            all_instances[zone] = response.instances
    return all_instances

def create_instance(
    project_id: str,
    zone: str,
    instance_name: str,
    machine_type: str = "n1-standard-1",
    source_image: str = "projects/debian-cloud/global/images/family/debian-10",
    network_name: str = "global/networks/default",
) -> compute_v1.Instance:
    instance_client = compute_v1.InstancesClient()
    operation_client = compute_v1.ZoneOperationsClient()

    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = (
        source_image  # "projects/debian-cloud/global/images/family/debian-10"
    )
    initialize_params.disk_size_gb = 10
    disk.initialize_params = initialize_params
    disk.auto_delete = True
    disk.boot = True
    disk.type_ = "PERSISTENT"

    # Use the network interface provided in the network_name argument.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = network_name

    # Collect information into the Instance object.
    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.disks = [disk]
    if re.match(r"^zones/[a-z\d\-]+/machineTypes/[a-z\d\-]+$", machine_type):
        instance.machine_type = machine_type
    else:
        instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"
    instance.network_interfaces = [network_interface]

    # Prepare the request to insert an instance.
    request = compute_v1.InsertInstanceRequest()
    request.zone = zone
    request.project = project_id
    request.instance_resource = instance

    # Wait for the create operation to complete.
    print(f"Creating the {instance_name} instance in {zone}...")
    operation = instance_client.insert_unary(request=request)
    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=zone, project=project_id
        )
    if operation.error:
        print("Error during creation:", operation.error, file=sys.stderr)
    if operation.warnings:
        print("Warning during creation:", operation.warnings, file=sys.stderr)
    print(f"Instance {instance_name} created.")
    return instance

def get_instance(project_id: str, name: str, zone: str) -> Instance | None:
    instance_client = compute_v1.InstancesClient()
    instance_list = instance_client.list(project=project_id, zone=zone)

    for instance in instance_list:
        if instance.name == name:
            return instance

    return None

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
def element_to_oslc_resource(element, resource):
    if isinstance(element, Bucket):
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryId, Literal(element.id)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryName, Literal(element.name)))
        resource.rdf.add((resource.uri, OSLC_CloudProvider.directoryStorageClass, Literal(element.storage_class)))
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