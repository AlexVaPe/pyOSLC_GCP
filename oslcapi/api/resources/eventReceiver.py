import json
import logging
from flask import request
from flask_restful import Resource

from oslcapi.api.helpers import generate_creation_event, generate_modification_event, generate_deletion_event
from oslcapi.store import my_store

log = logging.getLogger('tester.sub')


class EventReceived(Resource):
    def post(self):
        payload = json.loads(request.data)

        action = payload['action']

        if action == 'opened':
            return generate_creation_event(payload, my_store)

        elif action == 'edited':
            return generate_modification_event(payload, my_store)

        elif action == 'deleted':
            return generate_deletion_event(payload, my_store)

        else:
            return
