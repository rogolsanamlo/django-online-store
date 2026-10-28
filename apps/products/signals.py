from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Product


@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    """Remove the image file from storage when a product is deleted."""
    if instance.image_name:
        instance.image_name.delete(save=False)
