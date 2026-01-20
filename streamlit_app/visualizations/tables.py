import pandas as pd
import streamlit as st

def create_flow_intelligence_table(data):
    """
    Process flow intelligence data (dict of timeframes) into Net Flow, Avg Flow, Wallet Count tables.
    """
    if not data or not isinstance(data, dict):
        return None, None, None

    timeframes = ['5m', '1h', '6h', '12h', '1d', '7d']
    
    # Pre-process data to handle wrapped 'data' keys (e.g. {"5m": {"data": [...]}})
    processed_data = {}
    for tf in timeframes:
        if tf in data:
            val = data[tf]
            if isinstance(val, dict) and 'data' in val and isinstance(val['data'], list):
                processed_data[tf] = val['data']
            elif isinstance(val, list):
                processed_data[tf] = val

    available_tfs = list(processed_data.keys())
    
    if not available_tfs:
        return None, None, None

    def build_df(metric_suffix, metric_keys_legacy=None):
        # Try to parse "wide" format first (e.g. whale_net_flow_usd)
        categories = ['public_figure', 'top_pnl', 'whale', 'smart_trader', 'exchange', 'fresh_wallets']
        rows = {}
        
        # Check if data looks like wide format
        is_wide = False
        first_tf = available_tfs[0]
        if processed_data[first_tf]:
             sample = processed_data[first_tf][0]
             if any(f"whale{metric_suffix}" in sample for sample in processed_data[first_tf]):
                 is_wide = True
                 
        if is_wide:
            for cat in categories:
                label = cat.replace('_', ' ').title()
                rows[label] = {}
                for tf in available_tfs:
                    items = processed_data.get(tf, [])
                    if not items: continue
                    item = items[0]
                    
                    key = f"{cat}{metric_suffix}"
                    # Handle nulls
                    val = item.get(key)
                    if val is None: val = 0
                    rows[label][tf] = val
        else:
            # Fallback to "long" format logic
            if not metric_keys_legacy: return pd.DataFrame()
            
            for tf in available_tfs:
                for item in processed_data[tf]:
                    label = item.get('label') or item.get('category') or 'Unknown'
                    val = 0
                    for key in metric_keys_legacy:
                        if key in item:
                            val = item[key]
                            break
                    if label not in rows:
                        rows[label] = {}
                    rows[label][tf] = val
        
        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(rows, orient='index')
        # Reorder columns to match timeframes
        cols = [tf for tf in available_tfs if tf in df.columns]
        df = df[cols]
        return df

    # Metric keys
    net_flow_df = build_df('_net_flow_usd', ['net_flow_usd', 'net_flow'])
    avg_flow_df = build_df('_avg_flow_usd', ['avg_flow_usd', 'avg_flow'])
    wallet_df = build_df('_wallet_count', ['wallet_count', 'wallets', 'users'])

    return net_flow_df, avg_flow_df, wallet_df

def create_transfers_table(data):
    """
    Create transfers table sorted by transfer_value_usd desc, block_timestamp desc
    """
    # Handle wrapped response (e.g. Nansen {"data": [...]})
    if isinstance(data, dict) and 'data' in data:
        data = data['data']

    if not data or not isinstance(data, list):
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    
    # Ensure cols exist
    if df.empty:
        return df

    # Convert timestamps
    if 'block_timestamp' in df.columns:
        df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])
        
    # Sort
    sort_cols = []
    ascending = []
    
    if 'transfer_value_usd' in df.columns:
        sort_cols.append('transfer_value_usd')
        ascending.append(False)
    elif 'value_usd' in df.columns: # Fallback
        sort_cols.append('value_usd')
        ascending.append(False)
        
    if 'block_timestamp' in df.columns:
        sort_cols.append('block_timestamp')
        ascending.append(False)
        
    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=ascending)
        
    # Select relevant columns for display
    display_cols = [c for c in ['block_timestamp', 'from_address', 'to_address', 'transfer_value_usd', 'value_usd', 'transaction_hash'] if c in df.columns]
    return df[display_cols]
