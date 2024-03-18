import streamlit as st
import pandas as pd
import os
from google.cloud import bigquery, aiplatform
from google.protobuf import json_format, struct_pb2

# Set up Google Cloud credentials and project configuration
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/zacharynguyen/Documents/GitHub/2024/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection/key/e2e-fraud-detection-debf1c9863af.json"
PROJECT_ID = 'e2e-fraud-detection'
REGION = 'us-central1'
BQ_DATASET = 'fraud_dataset'
BQ_TABLE = 'prepped-data'
ENDPOINT_ID = '5892812777856172032'  # Actual endpoint ID
API_ENDPOINT = 'us-central1-aiplatform.googleapis.com'

# Initialize BigQuery and AI Platform clients
bq_client = bigquery.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)


# Define the function to fetch data from BigQuery
def fetch_data(n):
    sql_query = f"""
    SELECT * EXCEPT(Class, transaction_id, splits)
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE splits='TEST'
    LIMIT {n}
    """
    return bq_client.query(query=sql_query).to_dataframe()


# Define the function for making predictions with a custom-trained model
def predict_custom_trained_model_sample(project, endpoint_id, instances):
    client_options = {"api_endpoint": API_ENDPOINT}
    prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    endpoint_path = prediction_client.endpoint_path(project=project, location=REGION, endpoint=endpoint_id)
    instances = [json_format.ParseDict(instance, struct_pb2.Value()) for instance in instances]
    response = prediction_client.predict(endpoint=endpoint_path, instances=instances)

    return [dict(prediction) for prediction in response.predictions]


# Streamlit UI
st.title('Fraud Detection Prediction App')
st.write('This app predicts fraudulent transactions using a pre-trained machine learning model.')

n = st.number_input('Select the number of records to fetch for prediction:', min_value=1, value=10, step=1)

if st.button('Fetch Data & Predict'):
    with st.spinner('Fetching data...'):
        data = fetch_data(n)
        st.write('Fetched data:')
        st.dataframe(data.style.highlight_max(axis=0))

    with st.spinner('Making predictions...'):
        instances = data.to_dict(orient='records')
        predictions = predict_custom_trained_model_sample(PROJECT_ID, ENDPOINT_ID, instances)

        data['Predicted_Class'] = [p["predicted_Class"] for p in predictions]
        data['Class_Values'] = [str(p["Class_values"]) for p in predictions]  # Convert to string for display
        data['Class_Probs'] = [str(p["Class_probs"]) for p in predictions]  # Convert to string for display

        st.success('Predictions complete!')
        st.write('Data with Predictions:')
        st.dataframe(data.assign(hack='').set_index('hack'))
