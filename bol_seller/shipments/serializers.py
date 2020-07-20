from rest_framework.serializers import ModelSerializer

from .models import Seller


class SellerDetailSerializer(ModelSerializer):
    class Meta:
        model = Seller
        fields = ('id', 'first_name', 'last_name', 'shop_name', 'client_id', 'client_secret')
