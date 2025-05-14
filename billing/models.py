# billing/models.py

from django.db import models
from accounts.models import Lawyer
from cases.models import Case

class TimeLog(models.Model):
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='time_logs')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='time_logs')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600  # in hours
        return 0

    def __str__(self):
        return f"{self.lawyer} - {self.case} - {self.start_time} to {self.end_time or 'ongoing'}"


class Invoice(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='invoices')
    generated_at = models.DateTimeField(auto_now_add=True)
    total_hours = models.FloatField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_pdf = models.FileField(upload_to='invoices/', blank=True, null=True)

    def __str__(self):
        return f"Invoice for {self.case} on {self.generated_at.date()}"
