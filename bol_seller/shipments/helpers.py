import json
from .models import Shipment


def save_shipment_list(shipment_list):
    """
    Helper to detect new shipments and save them in the database
    """
    shipment_ids = [obj['shipmentId'] for obj in shipment_list]
    saved_shipments = Shipment.objects.filter(
        shipment_id__in=shipment_ids
    ).values_list('shipment_id', flat=True)

    new_shipment_ids = set(shipment_ids) - set(saved_shipments)
    new_shipments = filter(lambda x: x['shipmentId'] in new_shipment_ids, shipment_list)

    new_shipment_obj_list = []
    for shipment in new_shipments:
        shipment_dict = {
            'shipment_id': shipment['shipmentId'],
            'shipment_date': shipment['shipmentDate']
        }
        new_shipment_obj_list.append(Shipment(**shipment_dict))
    
    try:
        Shipment.objects.bulk_create(new_shipment_obj_list)
    except Exception as e:
        print(e)
