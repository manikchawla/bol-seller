import requests
import time
from bol_seller.shipments.models import Seller

def get_access_token(seller):
    data = {
        'client_id': seller.client_id,
        'client_secret': seller.client_secret
    }
    r = requests.post('https://login.bol.com/token?grant_type=client_credentials', data=data)
    return r.json()['access_token']


if __name__ == '__main__':
    seller = Seller.objects.get(pk=1)
    access_token = get_access_token(seller)

    size = 100

    for i in range(size):
        headers = { 
            "Accept":"application/vnd.retailer.v3+json", 
            "Authorization": "Bearer {}".format(access_token) 
        }
        r = requests.get('https://api.bol.com/retailer/shipments?fulfillmentmethod=FBR', headers=headers)

        print(i)
        if r.status_code == 401:
            print('---- 401 -----')
            access_token = get_access_token(seller)
        elif r.status_code == 429:
            print('---- 429 -----')
            time.sleep(int(r.headers['retry-after']))
        elif r.status_code == 200:
            print('---- 200 -----')
            if r.headers['x-ratelimit-remaining'] == '0':
                print('## rate limit 0 ##')
                time.sleep(int(r.headers['x-ratelimit-reset']))
        print()