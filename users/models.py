from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.URLField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_plus_member = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    query_history = models.TextField(null=True, blank=True)
    processed_documents = models.ManyToManyField('document_analysis.ExcelDocumentModel', blank=True)

    def __str__(self):
        return self.username
