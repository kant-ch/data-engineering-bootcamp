# Ref: https://cloud.google.com/bigquery/docs/samples/bigquery-load-table-dataframe

import json
import os
from datetime import datetime

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


keyfile = os.environ.get("KEYFILE_PATH")
service_account_info = json.load(open(keyfile))
credentials = service_account.Credentials.from_service_account_info(service_account_info)
project_id = "dataeng-384606"
client = bigquery.Client(
    project=project_id,
    credentials=credentials,
)

def upload(table_name, date_list=False, time_partition_bool=False):
    if time_partition_bool == True:
        job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=True,
                time_partitioning=bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field="created_at",
                )
            )
    else:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True
        )      

    file_path = f"./data/{table_name}.csv"
    df = pd.read_csv(file_path, parse_dates=date_list)
    df.info()

    table_id = f"{project_id}.deb_bootcamp.{table_name}"
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")

# Upload separately for events and orders tables due to different of datetime columns
upload("events",date_list=["created_at"],time_partition_bool=True)
upload("orders",date_list=["created_at","estimated_delivery_at","delivered_at"],time_partition_bool=True)

# Set non partition table list
non_partition_table = ["addresses","products","promos","order_items"]
for table_ in non_partition_table:
    upload(table_)
