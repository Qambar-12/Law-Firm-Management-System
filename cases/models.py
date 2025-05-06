from django.db import models
from accounts.models import LawFirm, Lawyer, Client
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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


class Document(models.Model):
    doc_id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')  # One-to-Many with Case
    doc_name = models.CharField(max_length=255)
    doc_path = models.FileField(upload_to='case_documents/',max_length=1024)
    doc_type = models.CharField(max_length=50, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Generic Foreign Key for uploaded_by (can reference LawFirm, Lawyer, or Client)
    uploaded_by_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    uploaded_by = GenericForeignKey('uploaded_by_content_type', 'uploaded_by_object_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doc_id', 'case'], name='unique_document_per_case')
        ]

    def __str__(self):
        return f"{self.doc_name} (Case: {self.case.case_title})"