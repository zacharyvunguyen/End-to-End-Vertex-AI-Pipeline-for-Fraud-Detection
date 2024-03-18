import os
import json
from google.cloud import bigquery, aiplatform
from google.protobuf import json_format, struct_pb2
from typing import Dict, List, Union

# Set Google Cloud credentials and project configuration
GOOGLE_APPLICATION_CREDENTIALS = "/Users/zacharynguyen/Documents/GitHub/2024/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection/key/e2e-fraud-detection-debf1c9863af.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
PROJECT_ID = 'e2e-fraud-detection'
REGION = 'us-central1'

# BigQuery source data configuration
BQ_PROJECT = PROJECT_ID
BQ_DATASET = 'fraud_dataset'
BQ_TABLE = 'prepped-data'
# Model Training
VAR_TARGET = 'Class'
VAR_OMIT = 'transaction_id' # add more variables to the string with space delimiters
# Initialize BigQuery and AI Platform clients
bq_client = bigquery.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)

# Define SQL query for fetching data
n = 1000  # Number of records to fetch
sql_query = f"""
SELECT * EXCEPT({VAR_TARGET}, {VAR_OMIT}, splits)
FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
WHERE splits='TEST'
LIMIT {n}
"""
print(sql_query)

# Execute the query and convert to DataFrame
pred_df = bq_client.query(query=sql_query).to_dataframe()
newobs = pred_df.to_dict(orient='records')

# Fix: Define the function for making predictions with a custom-trained model
def predict_custom_trained_model_sample(project: str, endpoint_id: str, instances: List[Dict],
                                        location: str = "us-central1",
                                        api_endpoint: str = "us-central1-aiplatform.googleapis.com"):
    client_options = {"api_endpoint": api_endpoint}
    prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Convert instances to the format expected by the AI Platform Predict API
    instances = [json_format.ParseDict(instance_dict, struct_pb2.Value()) for instance_dict in instances]

    # Construct endpoint path and make the prediction request
    endpoint_path = prediction_client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
    response = prediction_client.predict(endpoint=endpoint_path, instances=instances)

    # Print the deployed model ID and predictions
    print("response")
    print("deployed_model_id:", response.deployed_model_id)
    predictions = [dict(prediction) for prediction in response.predictions]
    for prediction in predictions:
        print("prediction:", prediction)

# Call the prediction function with a list of instances
predict_custom_trained_model_sample(
    project="993073267534",
    endpoint_id="5892812777856172032",
    location="us-central1",
    instances=newobs  # Pass the entire list of instances
)
