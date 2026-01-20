"""
Dune Analytics API Client
Uses official dune-client SDK for raw SQL execution
"""
import logging
try:
    from dune_client.client import DuneClient as OfficialDuneClient
except ImportError:
    OfficialDuneClient = None
from config import API_KEYS

# Suppress verbose dune_client logs
if OfficialDuneClient:
    logging.getLogger('dune_client').setLevel(logging.WARNING)


class DuneClient:
    def __init__(self, api_key=None):
        if OfficialDuneClient is None:
            raise ImportError("dune-client package is not installed. Please install it with: pip install dune-client")
        self.api_key = api_key or API_KEYS.get('DUNE_API_KEY')
        self.client = OfficialDuneClient(self.api_key)

    def run_sql(self, query_sql, timeout=300):
        """
        Execute raw SQL and return results.

        Args:
            query_sql: Raw SQL to execute
            timeout: Max seconds to wait (default: 300s)

        Returns:
            dict with 'rows' and 'metadata'
        """
        # Use official SDK's run_sql method
        result = self.client.run_sql(query_sql)

        # Extract rows and metadata from result
        rows = []
        metadata = {}

        if result.result:
            rows = result.result.rows or []
            if result.result.metadata:
                metadata = {
                    'column_names': result.result.metadata.column_names,
                    'column_types': result.result.metadata.column_types,
                    'row_count': result.result.metadata.row_count,
                    'execution_time_millis': result.result.metadata.execution_time_millis
                }

        return {
            'execution_id': result.execution_id,
            'state': str(result.state),
            'rows': rows,
            'metadata': metadata
        }

    def execute_query(self, query_id, params=None):
        """
        Execute an existing query by ID
        """
        if OfficialDuneClient is None:
             raise ImportError("dune-client package is not installed. Please install it with: pip install dune-client")
        from dune_client.query import QueryBase
        query = QueryBase(query_id=query_id)
        if params:
            query.params = params
        return self.client.execute_query(query)

    def get_latest_result(self, query_id):
        """
        Get latest cached result for a query
        """
        return self.client.get_latest_result(query_id)

    def get_execution_status(self, execution_id):
        """
        Get execution status
        """
        return self.client.get_execution_status(execution_id)

    def get_execution_results(self, execution_id):
        """
        Get execution results
        """
        return self.client.get_execution_results(execution_id)
