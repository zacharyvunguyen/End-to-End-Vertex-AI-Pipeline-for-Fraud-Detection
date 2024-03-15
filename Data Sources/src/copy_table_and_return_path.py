import sys
import os
from kfp.dsl import component, Output, Dataset
from typing import NamedTuple

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, "..")))


@component(
    base_image='python:3.9',
    packages_to_install=["google-cloud-bigquery", "google-cloud-bigquery-storage"]
)
def bq_table_prep_op(
        project: str,
        region: str,
        source_bq_table_id: str,
        out_bq_dataset_id: str,
        dataset_output: Output[Dataset]
) -> NamedTuple("Outputs", [("bigqueryOutputTable", str)]):
    from google.cloud import bigquery

    new_bq_table_id = f"{out_bq_dataset_id}.prepped-data"
    bqclient = bigquery.Client(project=project)

    query = f"""
    CREATE OR REPLACE TABLE `{new_bq_table_id}` AS
WITH add_id AS (
    SELECT
        *,
        GENERATE_UUID() AS transaction_id
    FROM
        `{source_bq_table_id}`
)
SELECT
    *,
    CASE
        WHEN MOD(ABS(FARM_FINGERPRINT(CAST(transaction_id AS STRING))), 10) < 8 THEN 'TRAIN'
        WHEN MOD(ABS(FARM_FINGERPRINT(CAST(transaction_id AS STRING))), 10) = 9 THEN 'VALIDATE'
        ELSE 'TEST'
    END AS splits
FROM
    add_id
    """

    response = bqclient.query(query)
    _ = response.result()

    bigqueryOutputTable = f"bq://{new_bq_table_id}"
    dataset_output.path = bigqueryOutputTable

    return NamedTuple("Outputs", [("bigqueryOutputTable", str)])(bigqueryOutputTable)
