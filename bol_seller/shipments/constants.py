SYNC_AFTER_MIN = 5
START_DETAIL_SYNC_AFTER_SEC = 30

BOL_GET_ACCESS_TOKEN_URL = 'https://login.bol.com/token?grant_type=client_credentials'
BOL_GET_SHIPMENTS_URL = 'https://api.bol.com/retailer/shipments?fulfilmentmethod={}&page={}'
BOL_GET_SHIPMENT_DETAIL = 'https://api.bol.com/retailer/shipments/{}'

class BolFulFilmentMethods(object):
    FBR = 'FBR'
    FBB = 'FBB'
