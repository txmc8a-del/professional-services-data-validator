# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

import ibis
from typing import List
from data_validation import clients
from data_validation.query_builder.query_builder import QueryBuilder

class PartitionRowBuilder:
    def __init__(
        self,
        primary_keys: List[str],
        data_client: ibis.backends.base.BaseBackend,
        schema_name: str,
        table_name: str,
        custom_query: str,
        query_builder: QueryBuilder,
    ) -> None:
        """Build a PartitionRowBuilder object to handle row-level validation filtering.

        Args:
            primary_keys (List[str]): Keys used to identify a row for validation.
            data_client (BaseBackend): The Ibis backend client.
            schema_name (str): The name of the schema.
            table_name (str): The name of the table.
            custom_query (str): Optional custom SQL query.
            query_builder (QueryBuilder): DVT QueryBuilder instance.
        """
        self.primary_keys = primary_keys
        self.query = self._compile_query(
            data_client, schema_name, table_name, custom_query, query_builder
        )

    def _compile_query(
        self,
        data_client: ibis.backends.base.BaseBackend,
        schema_name: str,
        table_name: str,
        custom_query: str,
        query_builder: QueryBuilder,
    ) -> ibis.Expr:
        """Compiles the initial Ibis expression with applied filters."""
        if table_name:
            table = clients.get_ibis_table(data_client, schema_name, table_name)
        else:
            table = clients.get_ibis_query(data_client, custom_query)
            
        # Apply filters defined in the QueryBuilder (e.g., WHERE clauses)
        compiled_filters = query_builder.compile_filter_fields(table)
        return table.filter(compiled_filters) if compiled_filters is not None else table

    def get_count(self) -> int:
        """Return a count of rows for the specified primary keys."""
        # We select the primary keys and perform a count
        return (
            self.query[self.primary_keys]
            .count()
            .to_pandas() # Ensure compatibility across different Ibis backends
        )# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

import ibis
from typing import List
from data_validation import clients
from data_validation.query_builder.query_builder import QueryBuilder

class PartitionRowBuilder:
    def __init__(
        self,
        primary_keys: List[str],
        data_client: ibis.backends.base.BaseBackend,
        schema_name: str,
        table_name: str,
        custom_query: str,
        query_builder: QueryBuilder,
    ) -> None:
        """Build a PartitionRowBuilder object to handle row-level validation filtering.

        Args:
            primary_keys (List[str]): Keys used to identify a row for validation.
            data_client (BaseBackend): The Ibis backend client.
            schema_name (str): The name of the schema.
            table_name (str): The name of the table.
            custom_query (str): Optional custom SQL query.
            query_builder (QueryBuilder): DVT QueryBuilder instance.
        """
        self.primary_keys = primary_keys
        self.query = self._compile_query(
            data_client, schema_name, table_name, custom_query, query_builder
        )

    def _compile_query(
        self,
        data_client: ibis.backends.base.BaseBackend,
        schema_name: str,
        table_name: str,
        custom_query: str,
        query_builder: QueryBuilder,
    ) -> ibis.Expr:
        """Compiles the initial Ibis expression with applied filters."""
        if table_name:
            table = clients.get_ibis_table(data_client, schema_name, table_name)
        else:
            table = clients.get_ibis_query(data_client, custom_query)
            
        # Apply filters defined in the QueryBuilder (e.g., WHERE clauses)
        compiled_filters = query_builder.compile_filter_fields(table)
        return table.filter(compiled_filters) if compiled_filters is not None else table

    def get_count(self) -> int:
        """Return a count of rows for the specified primary keys."""
        # We select the primary keys and perform a count
        return (
            self.query[self.primary_keys]
            .count()
            .to_pandas() # Ensure compatibility across different Ibis backends
        )

