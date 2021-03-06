import logging
from flask_rdf.flask import returns_rdf
from flask_restful import Resource
from rdflib import Graph

from oslcapi.store import my_store

log = logging.getLogger('tester.sub')


class ServiceProvider(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        for service_provider in my_store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                return service_provider.rdf

        return Graph()


class ServiceProviderCatalog(Resource):
    @returns_rdf
    def get(self):
        return my_store.catalog.rdf
