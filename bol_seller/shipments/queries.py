from .models import Seller


def query_all_sellers():
    return Seller.objects.all()


def query_seller_by_id(seller_id):
    return Seller.objects.filter(pk=seller_id).first()