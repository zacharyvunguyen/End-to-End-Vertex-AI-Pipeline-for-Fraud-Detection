import streamlit as st
import os
import pandas as pd
from google.cloud import bigquery, aiplatform
from google.protobuf import json_format, struct_pb2

# Set up Google Cloud credentials and project configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/zacharynguyen/Documents/GitHub/2024/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection/key/e2e-fraud-detection-debf1c9863af.json"
PROJECT_ID = 'e2e-fraud-detection'
REGION = 'us-central1'
BQ_DATASET = 'fraud_dataset'
BQ_TABLE = 'prepped-data'
ENDPOINT_ID = '5892812777856172032'  # Make sure to replace 'your_endpoint_id' with the actual endpoint ID
API_ENDPOINT = 'us-central1-aiplatform.googleapis.com'

# Initialize BigQuery and AI Platform clients outside the prediction function to avoid re-initialization on each call
bq_client = bigquery.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)


def fetch_data(n):
    # Define SQL query for fetching data
    sql_query = f"""
    SELECT * EXCEPT(Class, transaction_id, splits)
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE splits='TEST'
    LIMIT {n}
    """
    return bq_client.query(query=sql_query).to_dataframe()


def predict_custom_trained_model_sample(project, endpoint_id, instances, location="us-central1",
                                        api_endpoint=API_ENDPOINT):
    client_options = {"api_endpoint": api_endpoint}
    prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Convert instances to the format expected by the AI Platform Predict API
    instances = [json_format.ParseDict(instance, struct_pb2.Value()) for instance in instances]

    # Construct endpoint path and make the prediction request
    endpoint_path = prediction_client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
    response = prediction_client.predict(endpoint=endpoint_path, instances=instances)

    return [dict(prediction) for prediction in response.predictions]


# Streamlit UI
st.title('Model Prediction App')

n = st.number_input('Enter the number of records to fetch for prediction:', min_value=1, value=10, step=1)
predict_button = st.button('Predict')
project="993073267534"
endpoint_id="5892812777856172032"
location="us-central1"

if predict_button:
    with st.spinner('Fetching data and making predictions...'):
        data = fetch_data(n)
        instances = data.to_dict(orient='records')
        predictions = predict_custom_trained_model_sample(project, endpoint_id, instances, location)
        st.success('Prediction complete!')

        # Display predictions in a beautiful format
        for prediction in predictions:
            st.json(prediction)  # Using st.json to beautifully format the JSON output

