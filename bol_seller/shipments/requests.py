import requests

from .constants import BOL_GET_ACCESS_TOKEN_URL


class SellerRequestManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        try:
            self.access_token = self.get_access_token()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            print(e)

    def get_access_token(self):
        """
        Method to fetch access token for a client by credentials
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        r = requests.post(BOL_GET_ACCESS_TOKEN_URL, data=data)

        if r.json().get('access_token'):
            return r.json()['access_token']
        else:
            return None
    
    def make_get_request(self, url):
        """
        Method to make a get request with custom headers
        """
        if self.access_token:
            headers = { 
                "Accept":"application/vnd.retailer.v3+json", 
                "Authorization": "Bearer {}".format(self.access_token) 
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 401:
                self.access_token = self.get_access_token()
                response = requests.get(url, headers=headers)
                return response
            else:
                return response