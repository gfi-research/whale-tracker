"""
Configuration file for API keys
Copy this to config.py and add your actual API keys
"""

# API Keys - Add your keys here
API_KEYS = {
    'DEFILLAMA_API_KEY': '',  # Required for pro endpoints only
    'NANSEN_API_KEY': '',     # Required for all Nansen endpoints
    'COINGECKO_API_KEY': '',  # Required for pro endpoints only
    'DUNE_API_KEY': '',       # Required for all Dune endpoints
}

# API Base URLs
API_URLS = {
    'DEFILLAMA': 'https://pro-api.llama.fi',
    'NANSEN': 'https://api.nansen.ai/api/v1',
    'COINGECKO': 'https://pro-api.coingecko.com/api/v3',
    'DUNE': 'https://api.dune.com/api/v1'
}

# Data storage configuration
DATA_DIR = 'data'
CACHE_DURATION = 300  # 5 minutes in seconds

# Supported chains and their identifiers
SUPPORTED_CHAINS = {
    'Ethereum': 'ethereum',
    'Solana': 'solana',
    'Polygon': 'polygon-pos',
    'Arbitrum': 'arbitrum-one',
    'Base': 'base',
    'Optimism': 'optimistic-ethereum',
    'BSC': 'binance-smart-chain'
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
