from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import viewsets


router = DefaultRouter()
router.register(r'sellers', viewsets.SellerViewSet)

app_name = "shipments"
urlpatterns = [
    path('', include(router.urls))
]