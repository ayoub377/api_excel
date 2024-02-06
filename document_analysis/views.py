import logging
import os
from concurrent.futures import ThreadPoolExecutor

import chardet
import pandas as pd

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import ExcelDocumentModel
from .serializers import DocumentSerializer
from .prediction import TapasInference  # Import your TapasInference class
import uuid

from .utils import divide_csv, removeChunks


# function that gets loggers
def get_logger():
    logger = logging.getLogger(__name__)
    return logger


def process_chunk(chunk_path, query):
    result = chardet.detect(open(chunk_path, 'rb').read())
    df = pd.DataFrame(pd.read_csv(chunk_path, encoding=result['encoding']))
    df = df.astype(str)

    tapas_inference = TapasInference()
    query = query
    tapas_results = tapas_inference.predict(df, query)

    return tapas_results


class DocumentAnalysisView(APIView):
    logger = get_logger()

    def post(self, request, format=None):
        self.logger.info("DocumentAnalysisView post method called")
        temp_file_name_excel = f"temp_{uuid.uuid4().hex}.xlsx"
        temp_file_name_csv = f"temp_{uuid.uuid4().hex}.csv"

        # Check if the 'file' key is in the request data
        if 'file' not in request.data:
            self.logger.error("File not provided")
            return Response({'error': 'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save file temporarily
            with open(temp_file_name_excel, 'wb') as temp:
                temp.write(request.data['file'].read())

            # Convert Excel to CSV using Pandas
            excel_data = pd.read_excel(temp_file_name_excel)
            csv_data = excel_data.to_csv(index=False)
            # store csv file temporarily
            with open(temp_file_name_csv, 'w') as temp:
                temp.write(csv_data)

            # Create an instance of the model with processed data
            doc = ExcelDocumentModel.objects.create(
                document_name=request.data.get('document_name'),
                document=request.data['file'],
                processed_data=csv_data,  # Assign CSV data to processed_data field
            )

            # Delete temp file
            os.remove(temp_file_name_excel)
            os.remove(temp_file_name_csv)

            # Serialize the created instance for the response
            serializer = DocumentSerializer(doc)
            response_data = {
                'document_info': serializer.data,
            }
            self.logger.info("DocumentAnalysisView post method completed")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # remove the temp file
            os.remove(temp_file_name_excel)
            os.remove(temp_file_name_csv)
            # Handle any exceptions that might occur during file processing
            self.logger.error("DocumentAnalysisView post method failed")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # Read the stored CSV data from the database
            doc_id = request.query_params.get('doc_id')
            doc = ExcelDocumentModel.objects.get(pk=doc_id)

            # Read CSV data
            csv_data = doc.processed_data
            # save the csv file temporarily and try to find a way to have the name of file as unique using time or rand
            temp_file_name_csv = f"temp_{uuid.uuid4().hex}.csv"

            with open(temp_file_name_csv, 'w') as temp:
                temp.write(csv_data)

            try:
                results = []
                # split the csv file into chunks of 30 rows
                num_chunks = divide_csv(temp_file_name_csv, "chunks")

                if num_chunks == 1:
                    # If the CSV file has less than 20 rows, process it directly
                    tapas_results = process_chunk(temp_file_name_csv, request.query_params.get('tapas_queries'))
                    results.append(tapas_results)
                    response_data = {
                        'queries': tapas_results[0]['query'],
                        'predicted_answers': tapas_results[0]['predicted_answer']
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                # predict the tapas results for each chunk parallelly and then combine the results
                query = request.query_params.get('tapas_queries')
                with ThreadPoolExecutor() as executor:
                    # Submit tasks to process each chunk in parallel
                    futures = [executor.submit(process_chunk, os.path.join("chunks", chunk), query) for chunk in
                               os.listdir("chunks")]

                    # Wait for all threads to complete
                    for future in futures:
                        tapas_results = future.result()
                        results.extend(tapas_results)

                # remove the temp file
                removeChunks()
                # remove the temp file
                os.remove(temp_file_name_csv)
                # Combine the results
                queries = results[0]['query']
                predicted_answers = [result['predicted_answer'] for result in results]
                # Serialize the results for the response
                response_data = {
                    'queries': queries,
                    'predicted_answers': predicted_answers
                }

            except Exception as e:
                self.logger.error("DocumentAnalysisView get method failed")
                # remove the temp file
                os.remove(temp_file_name_csv)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(response_data, status=status.HTTP_200_OK)

        except ExcelDocumentModel.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle any exceptions that might occur during the prediction process
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
