# End to End Vertex AI Pipeline for Fraud Detection
 
## An AI-based Fraud Detection System

## Overview
The AI-based Fraud Detection System leverages Google Cloud's Vertex AI to deploy the most effective machine learning models for detecting fraudulent transactions in credit card data. This project encapsulates a workflow of training, evaluating, and deploying machine learning models in a cohesive pipeline, ensuring the deployment of the most accurate model available for fraud detection.

## Pipeline

### Deploying the Current Best Model to an Endpoint
The project structure organizes experiments in notebooks, each representing different machine learning techniques applied to the same dataset. This arrangement facilitates:
- Collaboration among multiple coworkers on the same project.
- Exploration of different approaches at various times.
- Continuous development and comparison of multiple techniques in parallel.

Each model iteration is registered in the Vertex AI Model Registry with a consistent label for `series`. This allows for routine evaluation of all model iterations to select the "current" best model for the domain.

#### Workflow Overview
1. **Candidate Selection Path:**
   - Fetch the list of candidate models from Vertex AI Model Registry, filtered by `labels.series={SERIES}` and `version_alias=default`.
   - Asynchronously loop over the list of candidate models to log metrics such as evaluation scores, confusion matrices, and ROC curves.
   - Select the best candidate model based on the gathered metrics.

2. **Current Model Review Path:**
   - Verify the existence of an endpoint, or create one if necessary.
   - Identify the deployed model receiving the most traffic.
   - If a model is currently deployed, gather its evaluation metrics.
   - If no model is deployed, proceed to deploy the best candidate model on the endpoint.

3. **Compare and Update Path:**
   - If the best candidate model outperforms the currently deployed model, replace the deployed model with the best candidate model.

#### Pipeline Implementation
This approach has been materialized into a Vertex AI Pipeline, enabling a serverless execution of the entire workflow. Each step of the outlined workflow is encapsulated into components that interact through defined inputs and outputs.

![Pipeline Dashboard](Media/pipeline.png)

### Pipelines
Pipelines represent workflows with multiple interdependent steps. Utilizing Vertex AI Pipelines, we can automate the model training, evaluation, and deployment process efficiently, treating each workflow step as a component within the pipeline.

### Prerequisites
- **BQML Models:** One or more BigQuery ML models that have been registered in the Vertex AI Model Registry.


## Contact

Zachary Nguyen - [@LinkedIn](https://www.linkedin.com/in/zacharyvunguyen/) - zacharynguyen.ds@gmail.com

Project Link: [https://github.com/zacharyvunguyen/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection](https://github.com/zacharyvunguyen/End-to-End-Vertex-AI-Pipeline-for-Fraud-Detection)

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Google Cloud Platform](https://cloud.google.com/)
