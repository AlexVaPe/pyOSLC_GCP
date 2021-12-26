from pyoslc_server import OSLCAPP
from adapter import RequirementAdapter, REQ_TO_RDF

app = OSLCAPP()

requirement_adapter = RequirementAdapter(
    identifier='adapter',
    title='Requirement Adapter',
    description='Requirement Adapter for OSLC',
    mapping=REQ_TO_RDF
)

app.api.add_adapter(requirement_adapter)
