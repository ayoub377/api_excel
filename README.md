# API for Excel Data Extraction using Natural Language
This project provides a RESTful API allowing users to upload Excel files and extract specific information from them using natural language queries. The backend is built using Django and Django REST Framework, and it uses [(https://huggingface.co/docs/transformers/en/model_doc/tapas)] to interpret natural language and retrieve relevant data from the Excel files.

## Features
  - Upload Excel files for analysis.
  - Extract information from Excel files using natural language.
  - Support for querying multiple types of data, including numbers, dates, and text.

## Installation

To install and run this project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/ayoub377/api_excel.git
```
### 2. Navigate to the project Directory
```bash
cd api_excel
```
### 3.Set Up Virtual Environment
```bash
python -m venv env
source env/bin/activate   # On Windows use `env\Scripts\activate`
```
### 4. Install dependencies
```bash
pip install -r requirements.txt
```
### 5.Apply migrations
```bash
python manage.py migrate
```
## 6. Run the server

```bash
python manage.py runserver
```
The API will be accessible at http://localhost:8000.

## API Endpoints

1. Upload an Excel File
  ```http
POST /api/excel/upload
```
Request: The file should be sent as a form-data file.
Response:
```json
{
  "id": "file_id",
  "message": "File uploaded successfully."
}
```
2. Query Excel File with Natural Language
   ```http
   POST /api/excel/{file_id}/query
   ```
   Resquest:
   ```json
   {
      "query": "What is the total sales in 2023?"
  }
   ```
Response:
```json
      {
        "answer": "The total sales in 2023 is $500,000."
      }
```
3. Get Uploaded Excel Files
    ```json
    GET /api/excel/files
    ```
Description: Retrieve a list of all uploaded Excel files.

Response:
```json
[
  {
    "id": "file_id",
    "filename": "sales_data.xlsx",
    "upload_date": "2024-09-12"
  }
]
```

## Technologies Used
   - Django: Python web framework.
   - Django REST Framework: Toolkit for building Web APIs.
   - Tapas: Table-based question-answering model for handling natural language queries.
   - Pandas: For Excel data manipulation.
   - OpenPyXL: For reading/writing Excel files.

## How It Works

   - Upload: Users upload Excel files via the /upload endpoint.
   - Natural Language Queries: Users ask questions in natural language, like "What is the total revenue in 2023?" The API processes this query and retrieves relevant data from the uploaded Excel file.
   - Response: The system uses Tapas to interpret the query and return the answer in JSON format.



