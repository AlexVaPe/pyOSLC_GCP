from oslcapi.models.oslc import OSLCStore
from oslcapi.models.trs import TRSStore

trs = TRSStore()
my_store = OSLCStore(trs)