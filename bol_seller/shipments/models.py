from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel

from .constants import BolFulFilmentMethods


class Seller(TimeStampedModel):
    first_name = models.CharField(_("Seller First Name"), max_length=255, blank=False, null=False)
    last_name = models.CharField(_("Seller Last Name"), max_length=255, blank=False, null=False)
    shop_name = models.CharField(_("Shop Name"), max_length=255, blank=False, null=False)
    client_id = models.CharField(_("Client ID"), max_length=100, blank=True, null=True)
    client_secret = models.CharField(_("Client Secret"), max_length=255, blank=True, null=True)
    last_synced_at = models.DateTimeField(_("Last synced at"), blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Shipment(TimeStampedModel):
    shipment_id = models.PositiveIntegerField(_("Shipment ID"), primary_key=True, blank=False, null=False)
    pickup_point = models.BooleanField(_("Pickup Point"), blank=True, null=True)
    shipment_date = models.DateTimeField(_("Shipment Date"), blank=False, null=False)
    shipment_reference = models.CharField(_("Shipment Reference"), max_length=32, blank=False, null=False)

    # Denormalized customer and billing details, TextField used in sqlite 
    # as an alternative for MySQL or PostgreSQL's JSONField
    customer_details = models.TextField(_("Customer Details"), blank=False, null=False)
    billing_details = models.TextField(_("Billing Address"), blank=False, null=False)
    detail_fetched = models.BooleanField(_("Is shipment detail fetched?"), blank=False, null=False,
        default=False)

    def __str__(self):
        return '{}'.format(self.shipment_id)


class Order(TimeStampedModel):
    order_id = models.CharField(_("Order ID"), primary_key=True, max_length=32, blank=False, null=False)
    order_date = models.DateTimeField(_("Order Date"), blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.order_id)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, _("Order"), blank=False, null=False)
    order_item_id = models.CharField(_("Order Item ID"), primary_key=True, max_length=32, blank=False,
        null=False)
    ean = models.CharField(_("European Article Number"), max_length=14, blank=False, null=False)
    title = models.CharField(_("Product Title"), max_length=255, blank=False, null=False)
    quantity = models.PositiveIntegerField(_("Quantity"), blank=False, null=False)
    offer_price = models.DecimalField(_("Offer Price"), max_digits=30, decimal_places=2, blank=False,
        null=False)
    offer_condition = models.CharField(_("Offer Condition"), max_length=32, blank=False, null=False)
    offer_reference = models.CharField(_("Offer Reference"), max_length=32, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.order_item_id)


class ShipmentItem(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
    order = models.ForeignKey(Order, _("Order"), blank=False, null=False)
    order_item = models.ForeignKey(OrderItem, _("Order Item"), blank=False, null=False)
    latest_delivery_date = models.DateTimeField(_("Last Delivery Date"), blank=False, null=False)
    FULFILMENT_METHOD_OPTIONS = (
        (BolFulFilmentMethods.FBR, 'FBR'),
        (BolFulFilmentMethods.FBB, 'FBB')
    )
    fulfilment_method = models.CharField(_("fulfilment Method"), choices=FULFILMENT_METHOD_OPTIONS,
        max_length=6, blank=False, null=False)
    
    def __str__(self):
        return '{} - {}'.format(self.shipment.id, self.order_item.title)


class Transport(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
    transport_id = models.CharField(_("Transport ID"), primary_key=True, max_length=32, blank=False, null=False)
    transporter_code = models.CharField(_("Transporter Code"), max_length=32, blank=False, null=False)
    track_and_trace = models.CharField(_("Track and Trace"), max_length=32, blank=False, null=False)

    # Shipping label could be a ForeignKey but for simplicity it is assumed part of the Transport
    shipping_label_id = models.CharField(_("Shipping Label ID"), max_length=32, blank=True, null=True)
    shipping_label_code = models.CharField(_("Shipping Label Code"), max_length=32, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.transport_id)
