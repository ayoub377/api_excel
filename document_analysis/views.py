import os
import io

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from dotenv import load_dotenv
import pandas as pd
from document_analysis.models import ExcelDocumentModel
from document_analysis.serializers import DocumentSerializer

load_dotenv()

openAiKey = os.environ.get('OPEN_AI_API_KEY')


from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import ExcelDocumentModel
from .serializers import DocumentSerializer
from .prediction import TapasInference  # Import your TapasInference class

class DocumentAnalysisView(APIView):
    def post(self, request, format=None):
        # Check if the 'file' key is in the request data
        if 'file' not in request.data:
            return Response({'error': 'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save file temporarily
            with open('temp.xlsx', 'wb') as temp:
                temp.write(request.data['file'].read())

            # Convert Excel to CSV using Pandas
            excel_data = pd.read_excel('temp.xlsx')
            csv_data = excel_data.to_csv(index=False)
            # store csv file temporarily
            with open('temp.csv', 'w') as temp:
                temp.write(csv_data)

            # Create an instance of the model with processed data
            doc = ExcelDocumentModel.objects.create(
                user=request.user,  # Assuming you have a user associated with the request
                document_name=request.data.get('document_name', 'Untitled Document'),
                document=request.data['file'],
                processed_data=csv_data,  # Assign CSV data to processed_data field
            )

            # Delete temp file
            os.remove('temp.xlsx')
            os.remove('temp.csv')

            # Serialize the created instance for the response
            serializer = DocumentSerializer(doc)
            response_data = {
                'document_info': serializer.data,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle any exceptions that might occur during file processing
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, format=None):
        try:

            # Read the stored CSV data from the database
            doc_id = request.query_params.get('doc_id')
            doc = ExcelDocumentModel.objects.get(pk=doc_id)

            # Read CSV data
            csv_data = doc.processed_data
            # save the csv file temporarily todo try to find a way to have the name of file as unique using time or rand
            with open('temp.csv', 'w') as temp:
                temp.write(csv_data)

            df = pd.DataFrame(pd.read_csv('temp.csv'))
            df = df.astype(str)

            # Extract Tapas queries from the request data
            query = request.query_params.get('tapas_queries', '')
            tapas_inference = TapasInference()
            tapas_results = tapas_inference.predict(df, query)

            response_data = {
                'tapas_results': tapas_results,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ExcelDocumentModel.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Handle any exceptions that might occur during the prediction process
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
