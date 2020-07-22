from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from django.utils import timezone
from django.db.models import Prefetch

from .serializers import (
    SellerDetailSerializer,
    ShipmentDetailSerializer
)
from .request_managers import SellerRequestManager
from .tasks import sync_shipment_list, sync_shipment_details
from .models import Seller, Shipment, Transport
from .constants import SYNC_AFTER_MIN, START_DETAIL_SYNC_AFTER_SEC


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SellerViewSet(ModelViewSet):
    """
    Viewset for seller endpoints
    """
    queryset = Seller.objects.all()
    serializer_class = SellerDetailSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        serialized_list = SellerDetailSerializer(Seller.objects.all(), many=True)
        return Response(serialized_list.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        serialized_obj = SellerDetailSerializer(Seller.objects.filter(pk=pk).first())
        return Response(serialized_obj.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serialized_obj = SellerDetailSerializer(data=data)
        serialized_obj.is_valid(raise_exception=True)
        self.perform_create(serialized_obj)
        return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None, *args, **kwargs):
        data = request.data.copy()
        seller = Seller.objects.filter(pk=pk).first()
        if seller:
            serialized_obj = SellerDetailSerializer(seller, data=data, partial=True)
            serialized_obj.is_valid(raise_exception=True)
            self.perform_update(serialized_obj)
            return Response(serialized_obj.data, status=status.HTTP_200_OK)
        return Response({'msg': 'Please send a valid Seller ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        seller = Seller.objects.filter(pk=pk).first()
        if seller:
            self.perform_destroy(seller)
            return Response({'msg': 'The object has been deleted'}, status=status.HTTP_200_OK)
        return Response({'msg': 'Please send a valid Seller ID'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def sync_shipments(self, request, pk=None, *args, **kwargs):
        """
        API Endpoint for starting shipment sync using a Celery task
        """
        seller = Seller.objects.filter(pk=pk).first()
        if seller:

            if not seller.last_synced_at or \
                timezone.now() - seller.last_synced_at > timezone.timedelta(minutes=SYNC_AFTER_MIN):
                
                request_manager = SellerRequestManager(seller.id, seller.client_id, seller.client_secret)
                sync_shipment_list.delay(request_manager)

                seller.last_synced_at = timezone.now()
                seller.save()
                return Response(
                    {'msg': 'Your shipments are getting synced'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'msg': 'Please request after {} min'.format(SYNC_AFTER_MIN)},
                    status=status.HTTP_200_OK
                )
        return Response(
            {'msg': 'Please send a valid Seller ID'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def list_shipments(self, request, pk=None, *args, **kwargs):
        if pk:
            shipments = Shipment.objects.filter(
                seller_id=pk, detail_fetched=True
            ).prefetch_related(
                'shipmentitem_set',
                'shipmentitem_set__order_item',
                'shipmentitem_set__order_item__order',
                Prefetch('transport_set', queryset=Transport.objects.all(), to_attr='prefetched_transport')
            )

            page = self.paginate_queryset(shipments)
            serialized_list = ShipmentDetailSerializer(page, many=True)
            return self.get_paginated_response(serialized_list.data)
        return Response({'msg': 'Please send a seller ID'}, status=status.HTTP_400_BAD_REQUEST)

