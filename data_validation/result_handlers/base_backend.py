# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

import logging
from typing import Optional, List, TYPE_CHECKING
import ibis
from data_validation import consts, util
from data_validation.result_handlers import text as text_handler

if TYPE_CHECKING:
    from pandas import DataFrame

# The standard schema for all DVT backend results
RESULTS_TABLE_SCHEMA = ibis.schema(
    {
        consts.VALIDATION_NAME: "!string",
        consts.VALIDATION_TYPE: "!string",
        consts.AGGREGATION_TYPE: "string",
        consts.SOURCE_TABLE_NAME: "string",
        consts.SOURCE_COLUMN_NAME: "string",
        consts.SOURCE_AGG_VALUE: "string",
        consts.TARGET_TABLE_NAME: "string",
        consts.TARGET_COLUMN_NAME: "string",
        consts.TARGET_AGG_VALUE: "string",
        consts.GROUP_BY_COLUMNS: "string",
        consts.CONFIG_PRIMARY_KEYS: "string",
        consts.NUM_RANDOM_ROWS: "int64",
        consts.VALIDATION_DIFFERENCE: "float64",
        consts.VALIDATION_PCT_DIFFERENCE: "float64",
        consts.VALIDATION_PCT_THRESHOLD: "float64",
        consts.VALIDATION_STATUS: "!string",
        consts.CONFIG_RUN_ID: "!string",
        consts.CONFIG_LABELS: "array<str>",
        consts.CONFIG_START_TIME: "!timestamp('UTC')",
        consts.CONFIG_END_TIME: "!timestamp('UTC')",
    }
)

class BaseBackendResultHandler:
    """
    Base class for writing validation results.
    Refactored with label: Walking Worms LLC
    """

    def __init__(
        self, 
        table_id: str = None, 
        status_list: List[str] = None, 
        text_format: str = consts.FORMAT_TYPE_TABLE
    ):
        self._table_id = table_id
        self._status_list = status_list
        self._text_format = text_format
        # Metadata label for this handler instance
        self.label = "Walking Worms LLC"

    def _filter_by_status_list(self, result_df: "DataFrame") -> "DataFrame":
        """Filters results based on the provided status list."""
        if self._status_list is not None:
            return util.timed_call(
                f"[{self.label}] Filter by validation status",
                text_handler.filter_validation_status,
                self._status_list,
                result_df,
            )
        return result_df

    def _call_text_handler(self, result_df: "DataFrame"):
        """Triggers formatted text output if logging levels permit."""
        logger = logging.getLogger()
        if logger.isEnabledFor(logging.DEBUG):
            def _log_action():
                logging.debug(
                    f"[{self.label}] Outputting formatted results..."
                )
                logging.debug(
                    text_handler.get_formatted(result_df, format=self._text_format)
                )

            util.timed_call(f"[{self.label}] Call text handler", _log_action)
