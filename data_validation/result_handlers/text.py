# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

from typing import TYPE_CHECKING, List, Optional
from data_validation import consts, util

if TYPE_CHECKING:
    from pandas import DataFrame

def filter_validation_status(status_list: List[str], result_df: "DataFrame") -> "DataFrame":
    """Filters the results based on status (e.g., 'success', 'fail')."""
    return result_df[result_df.validation_status.isin(status_list)]

def get_formatted(
    result_df: "DataFrame",
    output_format: str = consts.FORMAT_TYPE_TABLE,
    cols_filter_list: Optional[List[str]] = None,
) -> str:
    """Core logic to transform a DataFrame into various string formats."""
    cols_to_drop = cols_filter_list if cols_filter_list is not None else consts.COLUMN_FILTER_LIST
    
    # We drop metadata columns for human-readable formats (Text/Table)
    if output_format == consts.FORMAT_TYPE_TEXT:
        return result_df.drop(columns=cols_to_drop, errors="ignore").to_string(index=False)
    
    elif output_format == consts.FORMAT_TYPE_CSV:
        return result_df.to_csv(index=False, lineterminator="\n")
    
    elif output_format == consts.FORMAT_TYPE_JSON:
        return result_df.to_json(orient="records") # 'records' is usually more standard for JSON APIs
    
    # Default to Markdown/Table format
    return result_df.drop(columns=cols_to_drop, errors="ignore").to_markdown(
        tablefmt="fancy_grid", index=False
    )

class TextResultHandler:
    def __init__(
        self, 
        output_format: str, 
        status_list: Optional[List[str]] = None, 
        cols_filter_list: List[str] = consts.COLUMN_FILTER_LIST
    ):
        """
        Handles the output of validation results to the console or logs.
        
        Args:
            output_format: The format (text, csv, json, table).
            status_list: Optional list of statuses to include (e.g. ['fail']).
            cols_filter_list: Columns to exclude from visual reports.
        """
        self.output_format = output_format
        self.status_list = status_list
        self.cols_filter_list = cols_filter_list

    def _process_results(self, result_df: "DataFrame") -> str:
        """Internal logic to filter and format the DataFrame."""
        if self.status_list:
            result_df = filter_validation_status(self.status_list, result_df)

        # Validate format support before printing
        if self.output_format not in consts.FORMAT_TYPES:
            raise ValueError(
                f"Format [{self.output_format}] is not supported. "
                f"Supported formats: {consts.FORMAT_TYPES}"
            )

        formatted_output = get_formatted(result_df, self.output_format, self.cols_filter_list)
        print(formatted_output)
        return formatted_output

    def execute(self, result_df: "DataFrame") -> str:
        """Executes the handler and returns the formatted string."""
        return util.timed_call("Text handler output", self._process_results, result_df)
