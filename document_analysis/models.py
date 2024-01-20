from django.db import models

from users.models import CustomUser


class ExcelDocumentModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    document = models.FileField(upload_to='documents/')
    processed_data = models.TextField(blank=True, null=True)
    processing_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name
