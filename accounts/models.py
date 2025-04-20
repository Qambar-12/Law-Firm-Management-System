from django.db import models

# Create your models here.
class BaseUser(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Firm(BaseUser):
    firm_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'firm'
        app_label = 'none'

class Lawyer(BaseUser):
    lawyer_id = models.AutoField(primary_key=True)
    firm_id = models.ForeignKey(Firm, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'lawyer'
        app_label = 'none'

class Client(BaseUser):
    client_id = models.AutoField(primary_key=True)
    firm_id = models.ForeignKey(Firm, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'client'
        app_label = 'none'