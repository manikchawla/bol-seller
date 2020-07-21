import requests

from config import celery_app
from .constants import (
    BOL_GET_SHIPMENTS_URL,
    BOL_GET_SHIPMENT_DETAIL,
    BolFulFilmentMethods
)
from .models import Shipment
from .helpers import save_shipment_list, save_shipment_detail


@celery_app.task()
def sync_shipment_list(
    request_manager,
    fulfilment_method=BolFulFilmentMethods.FBR,
    page=1,
    fetched_both_methods=False):
    """
    Celery task to sync shipment list
    """

    fetch_next_page = True

    while fetch_next_page == True:
        url = BOL_GET_SHIPMENTS_URL.format(fulfilment_method, page)
        response = request_manager.make_get_request(url)

        if response.status_code == 200 and response.json() == {}:
            if fetched_both_methods == False:
                sync_shipment_list.delay(
                    request_manager, BolFulFilmentMethods.FBB, 1, True
                )
            fetch_next_page = False

        elif response.status_code == 200:
            page += 1
            save_shipment_list(request_manager.seller_id, response.json()['shipments'])
            if response.headers['x-ratelimit-remaining'] == '0':
                sync_shipment_list.apply_async(
                    (request_manager, fulfilment_method, page, fetched_both_methods),
                    countdown=int(response.headers['x-ratelimit-reset'])
                )
                fetch_next_page = False

        elif response.status_code == 429:
            sync_shipment_list.apply_async(
                (request_manager, fulfilment_method, page, fetched_both_methods),
                countdown=int(response.headers['retry-after'])
            )
            fetch_next_page = False


@celery_app.task()
def sync_shipment_details(request_manager):
    unfetched_shipments = Shipment.objects.filter(
        seller_id=request_manager.seller_id, detail_fetched=False
    )

    if unfetched_shipments.count() > 0:
        for counter, shipment in enumerate(unfetched_shipments):
            url = BOL_GET_SHIPMENT_DETAIL.format(shipment.shipment_id)
            response = request_manager.make_get_request(url)

            if response.status_code == 200:
                save_shipment_detail(response.json())
                if response.headers['x-ratelimit-remaining'] == '0':
                    sync_shipment_details.apply_async(
                        (request_manager,),
                        countdown=int(response.headers['x-ratelimit-reset'])
                    )
                    break
                elif counter == len(unfetched_shipments) - 1:
                    sync_shipment_details.delay(request_manager)

            elif response.status_code == 429:
                sync_shipment_details.apply_async(
                    (request_manager,),
                    countdown=int(response.headers['retry-after'])
                )
                break