from django.urls import path

from document_analysis import views

urlpatterns = [
    path('document-analysis/', views.DocumentAnalysisView.as_view(), name='index'),
]
