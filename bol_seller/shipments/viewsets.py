from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.utils import timezone

from .serializers import SellerDetailSerializer
from .queries import query_all_sellers, query_seller_by_id
from .requests import SellerRequestManager
from .tasks import sync_shipment_list
from .constants import SYNC_AFTER_MIN


class SellerViewSet(ModelViewSet):
    """
    Viewset for seller endpoints
    """
    queryset = query_all_sellers()
    serializer_class = SellerDetailSerializer

    def list(self, request, *args, **kwargs):
        serialized_list = SellerDetailSerializer(query_all_sellers(), many=True)
        return Response(serialized_list.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def create(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def update(self, request, pk=None, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=True, methods=['post'])
    def sync_shipments(self, request, pk=None, *args, **kwargs):
        """
        API Endpoint for starting shipment sync using a Celery task
        """
        seller = query_seller_by_id(pk)
        if seller and seller.client_id and seller.client_secret:

            if not seller.last_synced_at or \
                timezone.now() - seller.last_synced_at > timezone.timedelta(minutes=SYNC_AFTER_MIN):
                
                request_manager = SellerRequestManager(seller.client_id, seller.client_secret)
                sync_shipment_list.delay(request_manager)
                seller.last_synced_at = timezone.now()
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
            {'msg': 'Please send a valid Seller ID with Client ID and Client Secret'},
            status=status.HTTP_400_BAD_REQUEST
        )
