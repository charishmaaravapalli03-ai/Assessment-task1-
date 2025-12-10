import logging
import os
import io
import csv
import json
from datetime import datetime, timezone

import azure.functions as func
from azure.storage.blob import BlobServiceClient

REQUIRED_COLS = {"txn_id", "customer_id", "amount", "date"}
STORAGE_CONN_NAME = "AzureWebJobsStorage"

def move_blob(blob_service_client, target_container, target_path, data_bytes):
    target_client = blob_service_client.get_blob_client(
        container=target_container, blob=target_path
    )
    target_client.upload_blob(data_bytes, overwrite=True)

def delete_blob(blob_service_client, container, blob_name):
    try:
        client = blob_service_client.get_blob_client(
            container=container, blob=blob_name
        )
        client.delete_blob()
    except Exception as e:
        logging.warning(f"Delete failed: {e}")

def main(myblob: func.InputStream):
    logging.info(f"Triggered for: {myblob.name}")

    filename = os.path.basename(myblob.name)

    conn_str = os.environ[STORAGE_CONN_NAME]
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)

    data_bytes = myblob.read()
    text = data_bytes.decode("utf-8")

    csv_file = io.StringIO(text)
    reader = csv.DictReader(csv_file)

    valid = reader.fieldnames and REQUIRED_COLS.issubset(
        {c.strip() for c in reader.fieldnames}
    )

    processed_at = datetime.now(timezone.utc).isoformat()

    processed_path = f"processed-files/{filename}"
    invalid_path = f"invalid-files/{filename}"
    logs_path = f"logs/{filename}.json"

    if not valid:
        logging.info(f"INVALID CSV: Moving {filename} → invalid-files/")
        move_blob(blob_service_client, "raw-files", invalid_path, data_bytes)
        delete_blob(blob_service_client, "raw-files", filename)
        return

    csv_file.seek(0)
    reader2 = csv.reader(csv_file)
    next(reader2)
    rows = sum(1 for _ in reader2)

    move_blob(blob_service_client, "raw-files", processed_path, data_bytes)

    log_data = {
        "file": filename,
        "rows": rows,
        "processed_at": processed_at,
    }
    move_blob(
        blob_service_client,
        "raw-files",
        logs_path,
        json.dumps(log_data).encode("utf-8"),
    )

    delete_blob(blob_service_client, "raw-files", filename)

    logging.info(f"SUCCESS: {filename} processed.")
