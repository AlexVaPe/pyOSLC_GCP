import json
import logging
from flask import request
from flask_restful import Resource
from rdflib import Graph

from oslcapi.api.helpers import generate_creation_event, generate_modification_event, generate_deletion_event
from oslcapi.store import my_store

log = logging.getLogger('tester.sub')



class EventReceived(Resource):
    def post(self):
        log.warning('##### EVENT RECEIVED #####')
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
            service_provider = None
            # We retrieve the service provider
            if str(t).__contains__("Directory"):
                service_provider = next(service_provider for service_provider in my_store.catalog.service_providers if
                                        service_provider.module.description == 'FilesystemService')
            elif str(t).__contains__("Instance"):
                service_provider = next(service_provider for service_provider in my_store.catalog.service_providers if
                                        service_provider.module.description == 'VirtualMachineService')
            elif str(t).__contains__("Cluster"):
                service_provider = next(service_provider for service_provider in my_store.catalog.service_providers if
                                        service_provider.module.description == 'ContainerService')

            # Check the event type
            if str(t).__contains__("Create"):
                log.warning('##### CREATION EVENT #####')
                return generate_creation_event(graph, my_store, service_provider)
            elif str(t).__contains__("Modify"):
                log.warning('##### MODIFICATION EVENT #####')
                return generate_modification_event(graph, my_store, service_provider)
            elif str(t).__contains__("Delete"):
                log.warning('##### DELETION EVENT #####')
                return generate_deletion_event(graph, my_store, service_provider)
            else:
                return
