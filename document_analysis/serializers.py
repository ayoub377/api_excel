from rest_framework import serializers

from document_analysis.models import ExcelDocumentModel


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelDocumentModel
        fields = '__all__'
