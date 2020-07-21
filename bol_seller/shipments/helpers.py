import json
from .models import Shipment, ShipmentItem, Order, OrderItem, Transport


def save_shipment_list(seller_id, shipment_list):
    """
    Helper to detect new shipments and save them in the database
    """
    shipment_ids = [obj['shipmentId'] for obj in shipment_list]
    saved_shipments = Shipment.objects.filter(
        seller_id=seller_id, shipment_id__in=shipment_ids
    ).values_list('shipment_id', flat=True)

    new_shipment_ids = set(shipment_ids) - set(saved_shipments)
    new_shipments = filter(lambda x: x['shipmentId'] in new_shipment_ids, shipment_list)

    new_shipment_obj_list = []
    for shipment in new_shipments:
        shipment_dict = {
            'seller_id': seller_id,
            'shipment_id': shipment.get('shipmentId'),
            'shipment_date': shipment.get('shipmentDate')
        }
        new_shipment_obj_list.append(Shipment(**shipment_dict))
    
    try:
        Shipment.objects.bulk_create(new_shipment_obj_list)
    except Exception as e:
        print(e)


def save_shipment_detail(shipment_detail):
    """
    Helper to save shipment details in the database
    """
    shipment = Shipment.objects.filter(shipment_id=shipment_detail['shipmentId']).first()

    # Update shipment
    shipment.pickup_point = shipment_detail.get('pickupPoint')
    shipment.shipment_reference = shipment_detail.get('shipmentReference')
    shipment.billing_details = json.dumps(shipment_detail.get('billingDetails'))
    shipment.customer_details = json.dumps(shipment_detail.get('customerDetails'))
    shipment.detail_fetched = True
    shipment.save()

    # Create Transport if not created
    transport_obj, create = Transport.objects.get_or_create(
        shipment=shipment, transport_id=shipment_detail['transport']['transportId']
    )
    transport = shipment_detail['transport']

    transport_obj.shipping_label_id = transport.get('shippingLabelId')
    transport_obj.shipping_label_code = transport.get('shippingLabelCode')
    transport_obj.transport_id = transport.get('transportId')
    transport_obj.transporter_code = transport.get('transporterCode')
    transport_obj.track_and_trace = transport.get('trackAndTrace')
    transport_obj.shipment = shipment
    transport_obj.save()

    for item in shipment_detail['shipmentItems']:
        # Create order if not created
        order, created = Order.objects.get_or_create(order_id=item.get('orderId'), order_date=item.get('orderDate'))

        # Create OrderItem
        order_item_obj = {
            'order': order,
            'order_item_id': item.get('orderItemId'),
            'ean': item.get('ean'),
            'title': item.get('title'),
            'quantity': item.get('quantity'),
            'offer_price': item.get('offerPrice'),
            'offer_condition': item.get('offerCondition'),
            'offer_reference': item.get('offerReference')
        }
        order_item = OrderItem.objects.create(**order_item_obj)

        # Create ShipmentItem
        shipment_item_obj = {
            'shipment': shipment,
            'order': order,
            'order_item': order_item,
            'latest_delivery_date': item.get('latestDeliveryDate'),
            'fulfilment_method': item.get('fulfilmentMethod')
        }
        ShipmentItem.objects.create(**shipment_item_obj)
