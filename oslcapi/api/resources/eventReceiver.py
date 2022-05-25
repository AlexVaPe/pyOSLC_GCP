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
        log.warning("###   EVENT RECEIVED   ###")
        payload = json.loads(request.data.decode('utf-8'))
        log.warning("Payload: {}".format(json.dumps(payload, indent=4, sort_keys=True)))
        return 'OK', 200
