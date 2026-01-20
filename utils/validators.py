import re

def validate_contract_address(address, chain):
    """
    Validate contract address format based on chain
    """
    if not address:
        return False
        
    if chain in ['Ethereum', 'Polygon', 'Arbitrum', 'Base', 'Optimism', 'BSC']:
        # EVM address validation (starts with 0x and is 42 chars long)
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    if chain == 'Solana':
        # Solana address validation (base58, length 32-44)
        return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address))
        
    return True # Allow others for now
