import os

import chardet
import pandas as pd


def divide_csv(input_file, output_directory):
    result = chardet.detect(open(input_file, 'rb').read())

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(input_file, encoding = result['encoding'])

    # Get the number of rows in the DataFrame
    total_rows = len(df)

    # Define the maximum number of rows per file
    max_rows_per_file = 30

    # Calculate the number of chunks needed
    num_chunks = (total_rows // max_rows_per_file) + (1 if total_rows % max_rows_per_file != 0 else 0)

    # Split the DataFrame into chunks
    chunks = [df[i * max_rows_per_file:(i + 1) * max_rows_per_file] for i in range(num_chunks)]

    # Save each chunk as a separate CSV file
    for i, chunk in enumerate(chunks):
        output_file = os.path.join(output_directory, f"chunk_{i + 1}.csv")
        chunk.to_csv(output_file, index=False)

    return num_chunks


def removeChunks():
    for f in os.listdir("chunks"):
        os.remove(os.path.join("chunks", f))