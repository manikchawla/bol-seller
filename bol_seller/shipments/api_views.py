from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .queries import query_seller_by_id


class SyncShipments(APIView):
    """
    View to sync shipments for a seller, requires a valid seller ID
    """
    def post(self, request, format=None):
        if request.data.get('seller_id'):
            seller = query_seller_by_id(request.data.get('seller_id'))
            if seller and seller.client_key and seller.client_secret:
                # get access token
                # sync_now(seller)
                pass
            return Response(
                {'msg': 'Seller Client ID or Client Secret not set'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'msg': 'Please send a Seller ID'},
            status=status.HTTP_400_BAD_REQUEST
        )
