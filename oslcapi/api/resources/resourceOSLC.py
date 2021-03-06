import base64, json, logging, requests, xmltodict
from flask import request
from flask_rdf.flask import returns_rdf
from flask_restful import Resource
from rdflib import Graph, URIRef, Literal, Namespace, RDFS, RDF, plugin
from rdflib.serializer import Serializer
from kafka import KafkaProducer

from oslcapi.api.helpers.service_actions import create_resource, update_resource, delete_resource
from oslcapi.api.helpers import *
from oslcapi.store import my_store

log = logging.getLogger('tester.sub')

base_url = 'http://localhost:5001/GCP_OSLC/'
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')
event_endpoint = 'http://tfm-google.duckdns.org:5002/service/event/payload'

# Google Cloud Project ID
PROJECT_ID = "weighty-time-341718"

# Initialize Kafka producer
my_producer = KafkaProducer(
    bootstrap_servers = ['kafka:9092'],
    api_version=(0,11,5),
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
    )

class Directory_OSLCResource(Resource):
    @returns_rdf
    def get(self, service_provider_id, oslc_resource_id):
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return resource.rdf
        return Graph()

    @returns_rdf
    def put(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return update_resource(service_provider, resource, graph, my_store)

        return Graph()

    @returns_rdf
    def delete(self, service_provider_id, oslc_resource_id):
        return delete_resource(request.url, service_provider_id, oslc_resource_id)


class Directory_OSLCResourceList(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        g = Graph()
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    g += resource.rdf
        return g

    @returns_rdf
    def post(self, service_provider_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                return create_resource(service_provider, graph, my_store)[1]

        return Graph()


class VM_OSLCResource(Resource):
    @returns_rdf
    def get(self, service_provider_id, oslc_resource_id):
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return resource.rdf
        return Graph()

    @returns_rdf
    def put(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return update_resource(service_provider, resource, graph, my_store)

        return Graph()

    @returns_rdf
    def delete(self, service_provider_id, oslc_resource_id):
        return delete_resource(request.url)


class VM_OSLCResourceList(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        g = Graph()
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    g += resource.rdf
        return g

    @returns_rdf
    def post(self, service_provider_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                return create_resource(service_provider, graph, my_store)[1]

        return Graph()


class Cluster_OSLCResource(Resource):
    @returns_rdf
    def get(self, service_provider_id, oslc_resource_id):
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return resource.rdf
        return Graph()

    @returns_rdf
    def put(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return update_resource(service_provider, resource, graph, my_store)

        return Graph()

    @returns_rdf
    def delete(self, service_provider_id, oslc_resource_id):
        return delete_resource(request.url)


class Cluster_OSLCResourceList(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        g = Graph()
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    g += resource.rdf
        return g

    @returns_rdf
    def post(self, service_provider_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in my_store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                return create_resource(service_provider, graph, my_store)[1]

        return Graph()


class OSLCAction(Resource):
    @returns_rdf
    def get(self):
        g = Graph()
        for oslc_action in my_store.catalog.oslc_actions:
            g += oslc_action.rdf
        return g

    @returns_rdf
    def post(self):
        action = None
        actionProvider = None
        query_action = """

                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX oslc_actions: <http://open-services.net/ns/actions#>

                SELECT ?type

                WHERE {
                    ?s rdf:type ?type .
                }
            """

        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for t in graph.query(query_action):
            # We retreive the Action Provider and we create the action resource
            if str(t).__contains__("Directory"):
                for service_provider in my_store.catalog.service_providers:
                    if service_provider.module.description == 'FilesystemService':
                        actionProvider = service_provider
                action = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                        t.asdict()['type'].toPython())
            elif str(t).__contains__("Instance"):
                for service_provider in my_store.catalog.service_providers:
                    if service_provider.module.description == 'VirtualMachineService':
                        actionProvider = service_provider
                action = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                        t.asdict()['type'].toPython())

            elif str(t).__contains__("Cluster"):
                for service_provider in my_store.catalog.service_providers:
                    if service_provider.module.description == 'ContainerService':
                        actionProvider = service_provider
                action = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                        t.asdict()['type'].toPython())

            # DEMO SCENARIO 1
            if str(t).__contains__("Scenario1"):
                # VM creation
                for service_provider in my_store.catalog.service_providers:
                    if service_provider.module.description == 'VirtualMachineService':
                        actionProvider = service_provider

                ## ACTION 1
                action1 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                        t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action1.uri, OSLC_CloudProvider.instanceName, Literal('vm1-scenario1')))
                gr.add((action1.uri, OSLC_CloudProvider.instanceZone, Literal('us-central1-c')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

                ## ACTION 2
                action2 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                         t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action2.uri, OSLC_CloudProvider.instanceName, Literal('vm2-scenario1')))
                gr.add((action2.uri, OSLC_CloudProvider.instanceZone, Literal('us-central1-c')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

                ## ACTION 3
                action3 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                         t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action3.uri, OSLC_CloudProvider.instanceName, Literal('vm3-scenario1')))
                gr.add((action3.uri, OSLC_CloudProvider.instanceZone, Literal('us-central1-c')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

                # Buckets creation
                for service_provider in my_store.catalog.service_providers:
                    if service_provider.module.description == 'FilesystemService':
                        actionProvider = service_provider

                ## ACTION 4
                action4 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1,
                                                        str(actionProvider.id),
                                                        t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action4.uri, OSLC_CloudProvider.directoryName, Literal('bucket1-scenario1')))
                gr.add((action4.uri, OSLC_CloudProvider.directoryLocation, Literal('US')))
                gr.add((action4.uri, OSLC_CloudProvider.directoryStorageClass, Literal('STANDARD')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

                ## ACTION 5
                action5 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1,
                                                         str(actionProvider.id),
                                                         t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action5.uri, OSLC_CloudProvider.directoryName, Literal('bucket2-scenario1')))
                gr.add((action5.uri, OSLC_CloudProvider.directoryLocation, Literal('US')))
                gr.add((action5.uri, OSLC_CloudProvider.directoryStorageClass, Literal('STANDARD')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

                ## ACTION 6
                action6 = my_store.catalog.create_action(len(my_store.catalog.oslc_actions) + 1,
                                                         str(actionProvider.id),
                                                         t.asdict()['type'].toPython())
                gr = Graph()
                gr.add((action6.uri, OSLC_CloudProvider.directoryName, Literal('bucket3-scenario1')))
                gr.add((action6.uri, OSLC_CloudProvider.directoryLocation, Literal('US')))
                gr.add((action6.uri, OSLC_CloudProvider.directoryStorageClass, Literal('STANDARD')))
                resource, g = create_resource(actionProvider, gr, my_store)
                # Generate creation Event
                oslcEvent = generate_creation_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)

            elif str(t).__contains__("Create"):
                resource, g = create_resource(actionProvider, graph, my_store)
                event_graph = g
                if g is None:
                    action.add_result('KO')
                else:
                    action.add_result('OK')
                    # Generate creation Event
                    oslcEvent = generate_creation_event(resource, my_store)
                    oslcEvent_json = oslcEvent.serialize(format='json-ld')
                    # Send post to event server
                    my_producer.send('event-message', value=oslcEvent_json)
                    #r = requests.post(event_endpoint, data=oslcEvent_json)
                                      #headers={'Content-type': 'application/rdf+xml'})
                return g
            elif str(t).__contains__("Delete"):
                g, resource = delete_resource(actionProvider, graph, my_store)
                event_graph = g
                # Generate deletion Event
                oslcEvent = generate_deletion_event(resource, my_store)
                oslcEvent_json = oslcEvent.serialize(format='json-ld')
                event_graph.add((action.uri, RDF.type, Literal(action.action_type)))
                # Send post to event server
                my_producer.send('event-message', value=oslcEvent_json)
                #r = requests.post(event_endpoint, data=oslcEvent_json)
                                  #headers={'Content-type': 'application/rdf+xml'})
                return g

        return Graph()


class GCPLogs(Resource):
    def post(self):
        envelope = json.loads(request.data.decode('utf-8'))
        payload = base64.b64decode(envelope['message']['data'])

        try:
            json_msg = json.loads(payload)['protoPayload']['methodName']

            if ("create" or "delete") and "buckets" in json_msg:
                my_store.update_resources(my_store.catalog.service_providers[0], None, None)
            if ("insert" or "delete") and "instances" in json_msg:
                my_store.update_resources(None, my_store.catalog.service_providers[1], None)
        except:
            print("Useless message")

        # Returning any 2xx status indicates successful receipt of the message.
        return 'OK', 200
