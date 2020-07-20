from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Seller(TimeStampedModel):
    first_name = models.CharField(_("Seller First Name"), max_length=255, blank=False, null=False)
    last_name = models.CharField(_("Seller Last Name"), max_length=255, blank=False, null=False)
    shop_name = models.CharField(_("Shop Name"), max_length=255, blank=False, null=False)
    client_id = models.CharField(_("Client ID"), max_length=100, blank=True, null=True)
    client_secret = models.CharField(_("Client Secret"), max_length=255, blank=True, null=True)
    last_synced_at = models.DateTimeField(_("Last synced at"), blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)