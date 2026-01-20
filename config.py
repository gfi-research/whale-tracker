"""
Configuration file for API keys
"""
import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('config')

# Load .env file
load_dotenv()
logger.info("=== CONFIG LOADING ===")

# Try to load local settings first
try:
    from local_settings import API_KEYS as LOCAL_KEYS
    logger.info("LOCAL_KEYS: Loaded from local_settings.py")
except ImportError:
    LOCAL_KEYS = {}
    logger.info("LOCAL_KEYS: Not found (no local_settings.py)")

# Try to load Streamlit secrets
ST_SECRETS = {}
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        ST_SECRETS = dict(st.secrets.get("API_KEYS", {}))
        logger.info(f"ST_SECRETS: Found keys: {list(ST_SECRETS.keys())}")
    else:
        logger.info("ST_SECRETS: st.secrets not available")
except Exception as e:
    logger.info(f"ST_SECRETS: Error loading - {e}")

def get_key(name):
    # Order: Local Settings -> Streamlit Secrets -> Env Var -> Empty
    val = LOCAL_KEYS.get(name) or ST_SECRETS.get(name) or os.getenv(name) or ''
    source = "LOCAL" if LOCAL_KEYS.get(name) else "ST_SECRETS" if ST_SECRETS.get(name) else "ENV" if os.getenv(name) else "EMPTY"
    return val

# API Keys
API_KEYS = {
    'DEFILLAMA_API_KEY': get_key('DEFILLAMA_API_KEY'),
    'NANSEN_API_KEY': get_key('NANSEN_API_KEY'),
    'COINGECKO_API_KEY': get_key('COINGECKO_API_KEY'),
    'DUNE_API_KEY': get_key('DUNE_API_KEY'),
}

# Log API key status (masked)
for key, val in API_KEYS.items():
    status = f"{val[:8]}...{val[-4:]}" if len(val) > 12 else ("SET" if val else "EMPTY")
    logger.info(f"API_KEY {key}: {status}")

# API Base URLs
API_URLS = {
    'DEFILLAMA': 'https://coins.llama.fi',
    'DEFILLAMA_YIELDS': 'https://yields.llama.fi',
    'DEFILLAMA_API': 'https://api.llama.fi',
    'NANSEN': 'https://api.nansen.ai/api/v1',
    'COINGECKO': 'https://pro-api.coingecko.com/api/v3',
    'DUNE': 'https://api.dune.com/api/v1'
}

# Data storage configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DURATION = 300  # 5 minutes in seconds


# Try to load GCP_CONFIG from local settings
logger.info("=== GCP CONFIG ===")
try:
    from local_settings import GCP_CONFIG as LOCAL_GCP_CONFIG
    logger.info("GCP: Loaded from local_settings.py")
except ImportError:
    LOCAL_GCP_CONFIG = {}
    logger.info("GCP: No local_settings.py")

# Google Cloud Configuration
GCP_CREDENTIALS_DICT = None

# 1. Try Streamlit Secrets (for Cloud Deployment)
try:
    if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
        GCP_CREDENTIALS_DICT = dict(st.secrets['gcp_service_account'])
        logger.info(f"GCP: Found gcp_service_account in secrets, project_id={GCP_CREDENTIALS_DICT.get('project_id', 'N/A')}")
    else:
        logger.info("GCP: No gcp_service_account in st.secrets")
except Exception as e:
    logger.info(f"GCP: Error loading secrets - {e}")

# 2. Defaults (Local File)
DEFAULT_GCP_CONFIG = {
    'PROJECT_ID': 'gfi-455410',
    'SERVICE_ACCOUNT_FILE': os.path.join(BASE_DIR, 'gfi-455410-c5f5b0bf4d3a.json'),
    'GCS_BUCKET': 'gfi-token-tracker-data',
    'BIGQUERY_DATASET': 'token_tracker',
}

# 3. Merge with Local Settings
GCP_CONFIG = LOCAL_GCP_CONFIG or DEFAULT_GCP_CONFIG

# If we found secrets, inject them into config
if GCP_CREDENTIALS_DICT:
    GCP_CONFIG['CREDENTIALS_DICT'] = GCP_CREDENTIALS_DICT
    if 'project_id' in GCP_CREDENTIALS_DICT:
        GCP_CONFIG['PROJECT_ID'] = GCP_CREDENTIALS_DICT['project_id']
    logger.info(f"GCP: Using CREDENTIALS_DICT from Streamlit secrets")
else:
    logger.info(f"GCP: Using SERVICE_ACCOUNT_FILE: {GCP_CONFIG.get('SERVICE_ACCOUNT_FILE', 'N/A')}")

logger.info(f"GCP: PROJECT_ID={GCP_CONFIG.get('PROJECT_ID')}, BUCKET={GCP_CONFIG.get('GCS_BUCKET')}, DATASET={GCP_CONFIG.get('BIGQUERY_DATASET')}")

# Storage mode: 'local', 'gcs', 'bigquery', 'all'
STORAGE_MODE = get_key('STORAGE_MODE') or 'all'
logger.info(f"STORAGE_MODE: {STORAGE_MODE}")

# Source Icons Mapping (filename in assets folder)
SOURCE_ICONS = {
    'DefiLlama': 'defillama.jpg',
    'Nansen': 'nansen.jpg',
    'CoinGecko': 'coingecko.jpg',
    'Dune': 'dune.jpg'
}

# Supported chains and their identifiers (mapping to different API standards)
SUPPORTED_CHAINS = {
    'Ethereum': {
        'defillama': 'ethereum',
        'nansen': 'ethereum',
        'coingecko': 'ethereum',
        'id': 'ethereum'
    },
    'Solana': {
        'defillama': 'solana',
        'nansen': 'solana',
        'coingecko': 'solana',
        'id': 'solana'
    },
    'Polygon': {
        'defillama': 'polygon',
        'nansen': 'polygon',
        'coingecko': 'polygon-pos',
        'id': 'matic-network'
    },
    'Arbitrum': {
        'defillama': 'arbitrum',
        'nansen': 'arbitrum',
        'coingecko': 'arbitrum-one',
        'id': 'arbitrum'
    },
    'Base': {
        'defillama': 'base',
        'nansen': 'base',
        'coingecko': 'base',
        'id': 'base'
    },
    'Optimism': {
        'defillama': 'optimism',
        'nansen': 'optimism',
        'coingecko': 'optimistic-ethereum',
        'id': 'optimism'
    },
    'BSC': {
        'defillama': 'bsc',
        'nansen': 'bnb',
        'coingecko': 'binance-smart-chain',
        'id': 'binancecoin'
    }
}

# Default request timeout (seconds)
REQUEST_TIMEOUT = 30

# Rate limiting (requests per minute)
RATE_LIMITS = {
    'DEFILLAMA': 60,
    'NANSEN': 30,
    'COINGECKO': 50,
    'DUNE': 20
}
