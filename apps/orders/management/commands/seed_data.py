from django.core.management.base import BaseCommand

from apps.orders.models import OrderState, PaymentType
from apps.warehouses.models import WarehouseType


class Command(BaseCommand):
    help = "Create the lookup rows the shop needs (payment type, order state, warehouse types)."

    def handle(self, *args, **options):
        PaymentType.get_default()
        OrderState.get_paid()
        WarehouseType.get_input()
        WarehouseType.get_output()
        self.stdout.write(self.style.SUCCESS("Default lookup data is ready."))
