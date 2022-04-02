import base64
import json
import logging
from flask import request
from flask_rdf.flask import returns_rdf
from flask_restful import Resource
from rdflib import Graph, URIRef, Literal, Namespace, RDFS

from oslcapi.api.helpers.service_actions import create_resource, update_resource, delete_resource
from oslcapi.store import my_store

log = logging.getLogger('tester.sub')

base_url = 'http://localhost:5001/GCP_OSLC/'
OSLC_CloudProvider = Namespace('http://localhost:5001/GCP_OSLC/')

# Google Cloud Project ID
PROJECT_ID = "weighty-time-341718"

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
                return create_resource(service_provider, graph, my_store)

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
                return create_resource(service_provider, graph, my_store)

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
                return create_resource(service_provider, graph, my_store)

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

            if str(t).__contains__("Create"):
                g = create_resource(actionProvider, graph, my_store)
                if (g == None):
                    action.add_result('KO')
                else:
                    action.add_result('OK')
                return g
            elif str(t).__contains__("Delete"):
                return delete_resource(actionProvider, graph, my_store)

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
            # Clusters TBD
        except:
            print("Useless message")

        # Returning any 2xx status indicates successful receipt of the message.
        return 'OK', 200