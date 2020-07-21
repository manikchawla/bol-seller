import json
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    IntegerField,
    DecimalField,
    JSONField,
    SerializerMethodField,
)

from .models import Seller, Shipment, ShipmentItem, Transport


class SellerDetailSerializer(ModelSerializer):
    class Meta:
        model = Seller
        fields = ('id', 'first_name', 'last_name', 'shop_name', 'client_id', 'client_secret')


class ShipmentItemSerializer(ModelSerializer):
    order_id = CharField(source='order_item.order.order_id')
    order_date = CharField(source='order_item.order.order_date')
    order_item_id = CharField(source='order_item.order_item_id')
    ean = CharField(source='order_item.ean')
    title = CharField(source='order_item.title')
    quantity = IntegerField(source='order_item.quantity')
    offer_price = DecimalField(source='order_item.offer_price', max_digits=30, decimal_places=2)
    offer_condition = CharField(source='order_item.offer_condition')
    offer_reference = CharField(source='order_item.offer_reference')

    class Meta:
        model = ShipmentItem
        fields = (
            'order_item_id', 'order_id', 'order_date', 'latest_delivery_date',
            'ean', 'title', 'quantity', 'offer_price', 'offer_condition',
            'offer_reference', 'fulfilment_method'
        )


class TransportSerializer(ModelSerializer):
    class Meta:
        model = Transport
        fields = (
            'transport_id', 'transporter_code', 'track_and_trace', 'shipping_label_id',
            'shipping_label_code'
        )


class ShipmentDetailSerializer(ModelSerializer):
    shipment_items = SerializerMethodField()
    transport = SerializerMethodField()
    customer_details = SerializerMethodField()
    billing_details = SerializerMethodField()

    def get_shipment_items(self, obj):
        return ShipmentItemSerializer(obj.shipmentitem_set.all(), many=True).data
    
    def get_transport(self, obj):
        return TransportSerializer(obj.prefetched_transport[0]).data
    
    def get_customer_details(self, obj):
        return json.loads(obj.customer_details)
    
    def get_billing_details(self, obj):
        return json.loads(obj.billing_details)

    class Meta:
        model = Shipment
        fields = (
            'shipment_id', 'pickup_point', 'shipment_date', 'shipment_reference',
            'shipment_items', 'transport', 'customer_details', 'billing_details'
        )
