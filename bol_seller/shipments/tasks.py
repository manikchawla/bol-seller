import requests

from config import celery_app
from .constants import (
    BOL_GET_SHIPMENTS_URL,
    BolFulFillmentMethods
)
from .helpers import save_shipment_list


@celery_app.task()
def sync_shipment_list(
    request_manager,
    fulfillment_method=BolFulFillmentMethods.FBR,
    page=1,
    fetched_both_methods=False):
    """
    Celery task to sync shipment list
    """

    fetch_next_page = True

    while fetch_next_page == True:
        url = BOL_GET_SHIPMENTS_URL.format(fulfillment_method, page)
        response = request_manager.make_get_request(url)

        if response.status_code == 200 and response.json() == {}:
            if fetched_both_methods == False:
                sync_shipment_list.delay(
                    request_manager, BolFulFillmentMethods.FBB, 1, True
                )
            fetch_next_page = False

        elif response.status_code == 200:
            page += 1
            save_shipment_list(response.json()['shipments'])
            if response.headers['x-ratelimit-remaining'] == '0':
                sync_shipment_list.apply_async(
                    (request_manager, fulfillment_method, page, fetched_both_methods),
                    countdown=int(response.headers['x-ratelimit-reset'])
                )
                fetch_next_page = False

        elif response.status_code == 429:
            sync_shipment_list.apply_async(
                (request_manager, fulfillment_method, page, fetched_both_methods),
                countdown=int(response.headers['retry-after'])
            )
            fetch_next_page = False
        print()
