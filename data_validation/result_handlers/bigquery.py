# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

import logging
from typing import Optional, List
import google.oauth2.service_account
from pandas import DataFrame

from data_validation import clients, consts, exceptions, util
from data_validation.result_handlers.base_backend import BaseBackendResultHandler

BQRH_WRITE_MESSAGE = "Results written to BigQuery"
BQRH_NO_WRITE_MESSAGE = "No results to write to BigQuery (DataFrame empty or filtered)"

def credentials_from_key_path(sa_key_path: str):
    if not sa_key_path:
        return None
    return google.oauth2.service_account.Credentials.from_service_account_file(sa_key_path)

class BigQueryResultHandler(BaseBackendResultHandler):
    """Write results of data validation to BigQuery for persistent storage."""

    def __init__(
        self,
        bigquery_client,
        status_list: Optional[List[str]] = None,
        table_id: str = "pso_data_validator.results",
        text_format: str = consts.FORMAT_TYPE_TABLE,
    ):
        super().__init__()
        self._bigquery_client = bigquery_client
        self._table_id = table_id
        self._status_list = status_list
        self._text_format = text_format

    def _insert_bigquery(self, result_df: DataFrame):
        """Uploads the results DataFrame to the specified BigQuery table."""
        if result_df.empty:
            logging.info(BQRH_NO_WRITE_MESSAGE)
            return

        table = self._bigquery_client.get_table(self._table_id)
        # insert_rows_from_dataframe uses the BigQuery Storage Write API / Load Job logic
        chunk_errors = self._bigquery_client.insert_rows_from_dataframe(table, result_df)

        if any(chunk_errors):
            self._handle_insertion_errors(chunk_errors)

        run_id = result_df.iloc[0].get(consts.CONFIG_RUN_ID, "N/A")
        logging.info(f"{BQRH_WRITE_MESSAGE}, run id: {run_id}")

    def _handle_insertion_errors(self, errors: list):
        """Centralized logic for parsing BQ insertion errors, specifically for schema drift."""
        error_msg = str(errors)
        
        if "no
