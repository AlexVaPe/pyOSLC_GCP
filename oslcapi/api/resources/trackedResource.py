import logging

from flask_rdf.flask import returns_rdf
from flask_restful import Resource

from oslcapi.store import store

log = logging.getLogger('tester.sub')

class TrackedResourceSet(Resource):
    @returns_rdf
    def get(self):
        return store.trs.rdf

class TRSBase(Resource):
    @returns_rdf
    def get(self):
        return store.trs.base.rdf
    
class TRSChangeLog(Resource):
    @returns_rdf
    def get(self, change_log_id):
        return store.trs.change_logs[change_log_id-1].rdf