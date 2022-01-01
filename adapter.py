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
        if paging:
            offset = ((page_no - 1) * page_size)
            end = (offset + page_size)
            result = [vars(item) for item in self.items][offset:end]
        else:
            result = [vars(item) for item in self.items]
        # This is just an example, the code could be improved
        if select:
            final_result = []
            sel = [p.prop.split(":")[1] for p in select]
            sel.append('identifier')
            for r in result:
                final_result.append({k: v for k, v in r.items() if k in sel})
        else:
            final_result = result

        return len(self.items), final_result

    def creation_factory(self, item):
        r = Requirement(
            identifier=item.get('identifier'),
            title=item.get('title'),
            description=item.get('description'),
        )
        self.items.append(r)
        return r