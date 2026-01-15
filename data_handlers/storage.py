"""
Storage module for Token Tracker
Supports: Local JSON, Google Cloud Storage (GCS), BigQuery
"""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from config import DATA_DIR, GCP_CONFIG, STORAGE_MODE

# Setup logging
logger = logging.getLogger('storage')

# Lazy imports for GCP libraries
_gcs_client = None
_bq_client = None



def _get_gcs_client():
    """Get or create GCS client (lazy loading)"""
    global _gcs_client
    if _gcs_client is None:
        logger.info("=== GCS CLIENT INIT ===")
        from google.cloud import storage
        from google.oauth2 import service_account

        if 'CREDENTIALS_DICT' in GCP_CONFIG and GCP_CONFIG['CREDENTIALS_DICT']:
            # Use credentials from dict (Streamlit Secrets)
            logger.info("GCS: Using CREDENTIALS_DICT from Streamlit secrets")
            creds = service_account.Credentials.from_service_account_info(
                GCP_CONFIG['CREDENTIALS_DICT']
            )
            _gcs_client = storage.Client(
                credentials=creds,
                project=GCP_CONFIG['PROJECT_ID']
            )
            logger.info(f"GCS: Client created with project={GCP_CONFIG['PROJECT_ID']}")
        else:
            # Check if local file exists
            sa_file = GCP_CONFIG.get('SERVICE_ACCOUNT_FILE', '')
            if sa_file and os.path.exists(sa_file):
                logger.info(f"GCS: Using SERVICE_ACCOUNT_FILE: {sa_file}")
                _gcs_client = storage.Client.from_service_account_json(sa_file)
                logger.info("GCS: Client created from local JSON file")
            else:
                logger.warning(f"GCS: No credentials available! File not found: {sa_file}")
                raise FileNotFoundError(f"GCS credentials not available. Set gcp_service_account in Streamlit secrets or provide local file.")
    return _gcs_client


def _get_bq_client():
    """Get or create BigQuery client (lazy loading)"""
    global _bq_client
    if _bq_client is None:
        logger.info("=== BIGQUERY CLIENT INIT ===")
        from google.cloud import bigquery
        from google.oauth2 import service_account

        if 'CREDENTIALS_DICT' in GCP_CONFIG and GCP_CONFIG['CREDENTIALS_DICT']:
            # Use credentials from dict (Streamlit Secrets)
            logger.info("BigQuery: Using CREDENTIALS_DICT from Streamlit secrets")
            creds = service_account.Credentials.from_service_account_info(
                GCP_CONFIG['CREDENTIALS_DICT']
            )
            _bq_client = bigquery.Client(
                credentials=creds,
                project=GCP_CONFIG['PROJECT_ID']
            )
            logger.info(f"BigQuery: Client created with project={GCP_CONFIG['PROJECT_ID']}")
        else:
            # Check if local file exists
            sa_file = GCP_CONFIG.get('SERVICE_ACCOUNT_FILE', '')
            if sa_file and os.path.exists(sa_file):
                logger.info(f"BigQuery: Using SERVICE_ACCOUNT_FILE: {sa_file}")
                _bq_client = bigquery.Client.from_service_account_json(sa_file)
                logger.info("BigQuery: Client created from local JSON file")
            else:
                logger.warning(f"BigQuery: No credentials available! File not found: {sa_file}")
                raise FileNotFoundError(f"BigQuery credentials not available. Set gcp_service_account in Streamlit secrets or provide local file.")
    return _bq_client


def ensure_directory(path):
    """Create directory if not exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def _save_local(data, source, chain, address, endpoint_name, timestamp, user_id=None):
    """Save to local filesystem"""
    if user_id:
        directory = Path(DATA_DIR) / source / chain / address / user_id
    else:
        directory = Path(DATA_DIR) / source / chain / address
    ensure_directory(directory)

    filename = f"{endpoint_name}_{timestamp}.json"
    filepath = directory / filename

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

    return str(filepath)


def _save_gcs(data, source, chain, address, endpoint_name, timestamp, user_id=None):
    """Save to Google Cloud Storage"""
    try:
        client = _get_gcs_client()
        bucket = client.bucket(GCP_CONFIG['GCS_BUCKET'])

        # Create bucket if not exists
        if not bucket.exists():
            bucket = client.create_bucket(
                GCP_CONFIG['GCS_BUCKET'],
                location='asia-southeast1'
            )

        # Path: {source}/{chain}/{address}/{user_id}/{endpoint_name}_{timestamp}.json
        if user_id:
            blob_path = f"{source}/{chain}/{address}/{user_id}/{endpoint_name}_{timestamp}.json"
        else:
            blob_path = f"{source}/{chain}/{address}/{endpoint_name}_{timestamp}.json"
        blob = bucket.blob(blob_path)

        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type='application/json'
        )

        return f"gs://{GCP_CONFIG['GCS_BUCKET']}/{blob_path}"
    except Exception as e:
        logger.error(f"GCS save error: {e}")
        return {'error': str(e)}


def _save_bigquery(data, source, chain, address, endpoint_name, timestamp, user_id=None):
    """Save to BigQuery - Dataset per user: token_tracker_{user_id}"""
    try:
        client = _get_bq_client()
        project_id = GCP_CONFIG['PROJECT_ID']

        # Dataset name includes user_id: token_tracker_andrew, token_tracker_minh, etc.
        user_suffix = (user_id or 'unknown').lower().replace(' ', '_')
        dataset_id = f"{GCP_CONFIG['BIGQUERY_DATASET']}_{user_suffix}"

        # Create dataset if not exists
        dataset_ref = f"{project_id}.{dataset_id}"
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            from google.cloud import bigquery
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = 'asia-southeast1'
            client.create_dataset(dataset, exists_ok=True)

        # Table name: {source}_{endpoint_name} (sanitized)
        table_name = f"{source}_{endpoint_name}".replace('-', '_').lower()
        table_ref = f"{dataset_ref}.{table_name}"

        # Prepare row data (no user_id column needed - it's in dataset name)
        row = {
            'id': f"{chain}_{address}_{timestamp}",
            'chain': chain,
            'address': address,
            'timestamp': datetime.strptime(timestamp, "%Y%m%d_%H%M%S").isoformat(),
            'fetched_at': datetime.now().isoformat(),
            'raw_data': json.dumps(data),
        }

        # Create table if not exists
        from google.cloud import bigquery
        schema = [
            bigquery.SchemaField('id', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('chain', 'STRING'),
            bigquery.SchemaField('address', 'STRING'),
            bigquery.SchemaField('timestamp', 'TIMESTAMP'),
            bigquery.SchemaField('fetched_at', 'TIMESTAMP'),
            bigquery.SchemaField('raw_data', 'STRING'),
        ]

        try:
            client.get_table(table_ref)
        except Exception:
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table, exists_ok=True)

        # Insert row
        errors = client.insert_rows_json(table_ref, [row])
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
            return {'error': str(errors)}

        return table_ref
    except Exception as e:
        logger.error(f"BigQuery save error: {e}")
        return {'error': str(e)}


def _infer_bq_type(value):
    """Infer BigQuery type from Python value"""
    if value is None:
        return 'STRING'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    elif isinstance(value, int):
        return 'INTEGER'
    elif isinstance(value, float):
        return 'FLOAT'
    else:
        return 'STRING'


def save_dune_to_bigquery(rows_data, export_name, user_id=None):
    """
    Save Dune query results to BigQuery as proper table with columns.
    Each row of data becomes a separate BigQuery row.

    Args:
        rows_data: List of dicts from Dune query results
        export_name: Name for the table
        user_id: User identifier for dataset naming

    Returns:
        table_ref or {'error': message}
    """
    if not rows_data or len(rows_data) == 0:
        return {'error': 'No data to save'}

    try:
        from google.cloud import bigquery

        client = _get_bq_client()
        project_id = GCP_CONFIG['PROJECT_ID']

        # Dataset: token_tracker_{user_id}
        user_suffix = (user_id or 'unknown').lower().replace(' ', '_')
        dataset_id = f"{GCP_CONFIG['BIGQUERY_DATASET']}_{user_suffix}"

        # Create dataset if not exists
        dataset_ref = f"{project_id}.{dataset_id}"
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = 'asia-southeast1'
            client.create_dataset(dataset, exists_ok=True)

        # Table name from export_name (sanitized)
        table_name = f"dune_{export_name}".replace('-', '_').replace(' ', '_').lower()
        table_ref = f"{dataset_ref}.{table_name}"

        # Infer schema from first row
        first_row = rows_data[0]
        schema = []
        for col_name, value in first_row.items():
            bq_type = _infer_bq_type(value)
            # Sanitize column name
            safe_col = col_name.replace(' ', '_').replace('-', '_').lower()
            schema.append(bigquery.SchemaField(safe_col, bq_type, mode='NULLABLE'))

        # Add metadata columns
        schema.insert(0, bigquery.SchemaField('_ingested_at', 'TIMESTAMP', mode='NULLABLE'))

        # Create or replace table
        table = bigquery.Table(table_ref, schema=schema)

        # Delete existing table if exists, then create new
        try:
            client.delete_table(table_ref)
            logger.info(f"Deleted existing table: {table_ref}")
        except Exception:
            pass  # Table doesn't exist

        client.create_table(table)
        logger.info(f"Created table: {table_ref}")

        # Prepare rows with sanitized column names
        ingested_at = datetime.now().isoformat()
        prepared_rows = []
        for row in rows_data:
            prepared_row = {'_ingested_at': ingested_at}
            for col_name, value in row.items():
                safe_col = col_name.replace(' ', '_').replace('-', '_').lower()
                # Convert value to string if it's not a basic type
                if value is not None and not isinstance(value, (bool, int, float, str)):
                    value = str(value)
                prepared_row[safe_col] = value
            prepared_rows.append(prepared_row)

        # Insert rows in batches of 500
        batch_size = 500
        total_errors = []
        for i in range(0, len(prepared_rows), batch_size):
            batch = prepared_rows[i:i + batch_size]
            errors = client.insert_rows_json(table_ref, batch)
            if errors:
                total_errors.extend(errors)

        if total_errors:
            logger.error(f"BigQuery insert errors: {total_errors[:5]}")  # Log first 5 errors
            return {'error': f'{len(total_errors)} rows failed to insert'}

        logger.info(f"Inserted {len(prepared_rows)} rows to {table_ref}")
        return table_ref

    except Exception as e:
        logger.error(f"BigQuery Dune save error: {e}")
        return {'error': str(e)}


def save_json(data, source, chain, address, endpoint_name, user_id=None):
    """
    Save raw API response based on STORAGE_MODE

    Modes:
    - 'local': Save to local filesystem only
    - 'gcs': Save to GCS only
    - 'bigquery': Save to BigQuery only
    - 'all': Save to all destinations

    Args:
        user_id: Optional user identifier for multi-user support

    Returns: dict with paths/status for each destination
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}

    mode = STORAGE_MODE.lower()

    # Always save locally (for immediate access)
    if mode in ('local', 'all'):
        results['local'] = _save_local(data, source, chain, address, endpoint_name, timestamp, user_id)

    # Save to GCS
    if mode in ('gcs', 'all'):
        results['gcs'] = _save_gcs(data, source, chain, address, endpoint_name, timestamp, user_id)

    # Save to BigQuery
    if mode in ('bigquery', 'all'):
        results['bigquery'] = _save_bigquery(data, source, chain, address, endpoint_name, timestamp, user_id)

    # Return all results dict instead of single path
    return results


def _load_local(source, chain, address, endpoint_name, user_id=None):
    """Load from local filesystem"""
    if user_id:
        directory = Path(DATA_DIR) / source / chain / address / user_id
    else:
        directory = Path(DATA_DIR) / source / chain / address
    if not directory.exists():
        return None

    files = list(directory.glob(f"{endpoint_name}_*.json"))
    if not files:
        return None

    latest_file = sorted(files)[-1]
    with open(latest_file, 'r') as f:
        return json.load(f)


def _load_gcs(source, chain, address, endpoint_name, user_id=None):
    """Load latest from GCS"""
    try:
        client = _get_gcs_client()
        bucket = client.bucket(GCP_CONFIG['GCS_BUCKET'])

        if user_id:
            prefix = f"{source}/{chain}/{address}/{user_id}/{endpoint_name}_"
        else:
            prefix = f"{source}/{chain}/{address}/{endpoint_name}_"
        blobs = list(bucket.list_blobs(prefix=prefix))

        if not blobs:
            return None

        # Sort by name (timestamp) and get latest
        latest_blob = sorted(blobs, key=lambda b: b.name)[-1]
        content = latest_blob.download_as_string()
        return json.loads(content)
    except Exception as e:
        print(f"GCS load error: {e}")
        return None


def _load_bigquery(source, chain, address, endpoint_name, user_id=None):
    """Load latest from BigQuery - Dataset per user: token_tracker_{user_id}"""
    try:
        client = _get_bq_client()
        project_id = GCP_CONFIG['PROJECT_ID']

        # Dataset name includes user_id
        user_suffix = (user_id or 'unknown').lower().replace(' ', '_')
        dataset_id = f"{GCP_CONFIG['BIGQUERY_DATASET']}_{user_suffix}"
        table_name = f"{source}_{endpoint_name}".replace('-', '_').lower()

        query = f"""
        SELECT raw_data
        FROM `{project_id}.{dataset_id}.{table_name}`
        WHERE chain = @chain AND address = @address
        ORDER BY timestamp DESC
        LIMIT 1
        """

        from google.cloud import bigquery
        params = [
            bigquery.ScalarQueryParameter('chain', 'STRING', chain),
            bigquery.ScalarQueryParameter('address', 'STRING', address),
        ]

        job_config = bigquery.QueryJobConfig(query_parameters=params)

        result = client.query(query, job_config=job_config).result()
        for row in result:
            return json.loads(row.raw_data)
        return None
    except Exception as e:
        print(f"BigQuery load error: {e}")
        return None


def load_latest_json(source, chain, address, endpoint_name, user_id=None):
    """
    Load the most recent data for a given endpoint

    Args:
        user_id: Optional user identifier for multi-user support

    Priority: Local -> GCS -> BigQuery
    """
    # Try local first (fastest)
    data = _load_local(source, chain, address, endpoint_name, user_id)
    if data:
        return data

    # Try GCS
    if STORAGE_MODE in ('gcs', 'all'):
        data = _load_gcs(source, chain, address, endpoint_name, user_id)
        if data:
            return data

    # Try BigQuery
    if STORAGE_MODE in ('bigquery', 'all'):
        data = _load_bigquery(source, chain, address, endpoint_name, user_id)
        if data:
            return data

    return None


def list_stored_tokens():
    """List all tokens that have been stored"""
    tokens = []

    # Check local storage
    data_path = Path(DATA_DIR)
    if data_path.exists():
        for source_dir in data_path.iterdir():
            if source_dir.is_dir():
                for chain_dir in source_dir.iterdir():
                    if chain_dir.is_dir():
                        for address_dir in chain_dir.iterdir():
                            if address_dir.is_dir():
                                tokens.append({
                                    'source': source_dir.name,
                                    'chain': chain_dir.name,
                                    'address': address_dir.name
                                })

    return tokens


def get_storage_stats():
    """Get storage statistics"""
    stats = {
        'local': {'enabled': STORAGE_MODE in ('local', 'all'), 'count': 0},
        'gcs': {'enabled': STORAGE_MODE in ('gcs', 'all'), 'count': 0},
        'bigquery': {'enabled': STORAGE_MODE in ('bigquery', 'all'), 'count': 0},
    }

    # Count local files
    data_path = Path(DATA_DIR)
    if data_path.exists():
        stats['local']['count'] = len(list(data_path.rglob('*.json')))

    return stats
