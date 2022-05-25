import json
import logging
from flask import request
from flask_restful import Resource
from rdflib import Graph

from oslcapi.api.helpers import generate_creation_event, generate_modification_event, generate_deletion_event
from oslcapi.store import my_store

log = logging.getLogger('tester.event')



class EventReceived(Resource):
    def post(self):
        log.info("###   EVENT RECEIVED   ###")
        '''query_action = """

                        PREFIX oslc_events: <http://open-services.net/ns/events#>
                        PREFIX dc: <http://purl.org/dc/terms/>

                        SELECT ?type ?identifier

                        WHERE {
                            ?s oslc_events:Event ?type .
                            ?s dc:identifier ?identifier .
                        }
                    """

        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for t, id in graph.query(query_action):
            print("{} Received".format(str(t)))
            print(" * Description: {}".format(str(id)))'''
        payload = json.loads(request.data.decode('utf-8'))
        log.info("Payload: {}".format(json.dumps(payload, indent=4, sort_keys=True)))
        return 'OK', 200
