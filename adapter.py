from pyoslc_server.specification import ServiceResourceAdapter

from pyoslc.vocabularies.rm import OSLC_RM
from rdflib import DCTERMS
from resource import REQSTORE

REQ_TO_RDF = {
    "identifier": DCTERMS.identifier,
    "title": DCTERMS.title,
    "description": DCTERMS.description,
}

class RequirementAdapter(ServiceResourceAdapter):
    
    domain = OSLC_RM
    mapping = REQ_TO_RDF
    items = REQSTORE
    
    def __init__(self, **kwargs):
        super(RequirementAdapter, self).__init__(**kwargs)
        self.types = [OSLC_RM.Requirement]
    
    def query_capability(self, paging=False, page_size=50, page_no=1,
                         prefix=None, where=None, select=None,
                         *args, **kwargs):
        return len(self.items), [vars(item) for item in self.items]
