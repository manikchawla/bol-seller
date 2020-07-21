from .models import Seller


def query_all_sellers():
    return Seller.objects.all()