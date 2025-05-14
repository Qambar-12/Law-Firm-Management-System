import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Invoice

@receiver(post_delete, sender=Invoice)
def delete_invoice_file(sender, instance, **kwargs):
    if instance.invoice_pdf and instance.invoice_pdf.path:
        try:
            if os.path.isfile(instance.invoice_pdf.path):
                os.remove(instance.invoice_pdf.path)
        except Exception:
            pass
