import logging

from flask import request
from flask_rdf.flask import returns_rdf
from flask_restful import Resource
from rdflib import Graph

from oslcapi.api.helpers.service_actions import create_resource, update_resource, delete_resource
from oslcapi.store import store

log = logging.getLogger('tester.sub')


class OSLCResource(Resource):
    @returns_rdf
    def get(self, service_provider_id, oslc_resource_id):
        for service_provider in store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return resource.rdf
        return Graph()

    @returns_rdf
    def put(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return update_resource(service_provider, resource, graph, store)

        return Graph()

    @returns_rdf
    def delete(self, service_provider_id, oslc_resource_id):
        return delete_resource(request.url)


class OSLCResourceList(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        g = Graph()
        for service_provider in store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    g += resource.rdf
        return g

    @returns_rdf
    def post(self, service_provider_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                return create_resource(service_provider, graph, store)

        return Graph()