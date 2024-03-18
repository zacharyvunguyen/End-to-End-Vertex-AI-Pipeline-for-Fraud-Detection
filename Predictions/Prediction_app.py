import streamlit as st
import pandas as pd
import os
from google.cloud import bigquery, aiplatform
from google.protobuf import json_format, struct_pb2

# Set Google Cloud credentials and project configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/zacharynguyen/Documents/GitHub/2024/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection/key/e2e-fraud-detection-debf1c9863af.json"
PROJECT_ID = 'e2e-fraud-detection'
REGION = 'us-central1'
BQ_DATASET = 'fraud_dataset'
BQ_TABLE = 'prepped-data'
ENDPOINT_ID = '5892812777856172032'
API_ENDPOINT = 'us-central1-aiplatform.googleapis.com'

# Initialize BigQuery and AI Platform clients
bq_client = bigquery.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)

def fetch_data(n):
    """Fetches data from BigQuery."""
    sql_query = f"""
    SELECT * EXCEPT(Class, transaction_id, splits)
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE splits='TEST'
    LIMIT {n}
    """
    return bq_client.query(query=sql_query).to_dataframe()

def predict_custom_trained_model_sample(project, endpoint_id, instances):
    """Makes predictions using a custom-trained model."""
    client_options = {"api_endpoint": API_ENDPOINT}
    prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    endpoint_path = prediction_client.endpoint_path(project=project, location=REGION, endpoint=endpoint_id)
    instances = [json_format.ParseDict(instance, struct_pb2.Value()) for instance in instances]
    response = prediction_client.predict(endpoint=endpoint_path, instances=instances)
    return [dict(prediction) for prediction in response.predictions]

def highlight_fraud(row):
    """Highlights the row if the predicted class is '1'."""
    return ['background-color: yellow' if val == '1' else '' for val in row]

# Streamlit UI setup
st.title('Fraud Detection with AI')
st.header('Predict fraudulent transactions in real-time')

n = st.number_input('Number of transactions to analyze:', min_value=1, value=100, step=1)

if st.button('Analyze Transactions'):
    with st.spinner('Fetching transactions...'):
        data = fetch_data(n)
        st.write('Transactions fetched:')
        st.dataframe(data)

        instances = data.to_dict(orient='records')
        predictions = predict_custom_trained_model_sample(PROJECT_ID, ENDPOINT_ID, instances)

        # Adding prediction results to the DataFrame
        data['Predicted_Class'] = [pred["predicted_Class"] for pred in predictions]
        data['Class_Values'] = [", ".join(pred["Class_values"]) for pred in predictions]  # Joining list into comma-separated string
        data['Class_Probs'] = [", ".join(map(str, pred["Class_probs"])) for pred in predictions]  # Joining list into comma-separated string

        st.success('Predictions complete!')
        st.write('Analysis results:')

        # Apply the highlight function for each row based on 'Predicted_Class'
        st.dataframe(data.style.apply(highlight_fraud, subset=['Predicted_Class'], axis=1))

st.markdown('### Instructions')
st.markdown('1. Enter the number of recent transactions you wish to analyze for fraud detection.')
st.markdown('2. Click on **Analyze Transactions** to fetch the data and view the predictive analysis.')
st.markdown('Rows highlighted in yellow indicate transactions predicted as fraudulent.')

st.markdown('---')
st.markdown('Developed by the Fraud Detection Team')
