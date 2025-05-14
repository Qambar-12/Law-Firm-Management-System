from django.db import models

# ------------------------
# LAW FIRM MODEL
# ------------------------
class LawFirm(models.Model):
    lawfirm_id = models.AutoField(primary_key=True)
    lawfirm_name = models.CharField(max_length=255)
    lawfirm_email = models.EmailField(unique=True)
    lawfirm_contact = models.CharField(max_length=20)
    lawfirm_address = models.TextField()
    password = models.CharField(max_length=128)  # store hashed passwords
    lawfirm_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.lawfirm_name

# ------------------------
# LAWYER MODEL
# ------------------------
class Lawyer(models.Model):
    lawyer_id = models.AutoField(primary_key=True)
    lawfirm = models.ForeignKey(LawFirm, on_delete=models.CASCADE, related_name='lawyers')

    lawyer_name = models.CharField(max_length=200)
    lawyer_email = models.EmailField()
    lawyer_contact = models.CharField(max_length=20)
    lawyer_specialization = models.CharField(max_length=255)
    lawyer_hire_date = models.DateField()
    lawyer_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    lawyer_profile_picture = models.ImageField(upload_to='lawyer_profiles/', null=True, blank=True)
    lawyer_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lawyer_id', 'lawfirm'], name='unique_lawyer_per_lawfirm')
        ]

    def __str__(self):
        return self.lawyer_name


# ------------------------
# CLIENT MODEL
# ------------------------
class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    lawfirm = models.ForeignKey(LawFirm, on_delete=models.CASCADE, related_name='clients')

    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_contact = models.CharField(max_length=20)
    client_address = models.TextField()
    client_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client_id', 'lawfirm'], name='unique_client_per_lawfirm')
        ]

    def __str__(self):
        return self.client_name

