from django.db import models
from accounts.models import LawFirm, Lawyer, Client

class Case(models.Model):
    case_id = models.AutoField(primary_key=True)
    lawfirm = models.ForeignKey(LawFirm, on_delete=models.CASCADE, related_name='cases')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases')
    lawyers = models.ManyToManyField(Lawyer, blank=True, related_name='cases')
    case_title = models.CharField(max_length=255)
    case_description = models.TextField()
    case_type = models.CharField(max_length=100)
    case_status = models.CharField(max_length=50, default='Active')  
    case_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['case_id', 'lawfirm'], name='unique_case_per_lawfirm')
        ]

    def __str__(self):
        return f"{self.case_title} (Client: {self.client.client_name})"
