SYNC_AFTER_MIN = 5

BOL_GET_ACCESS_TOKEN_URL = 'https://login.bol.com/token?grant_type=client_credentials'
BOL_GET_SHIPMENTS_URL = 'https://api.bol.com/retailer/shipments?fulfillmentmethod={}&page={}'

class BolFulFillmentMethods(object):
    FBR = 'FBR'
    FBB = 'FBB'
