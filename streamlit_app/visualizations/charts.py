import plotly.graph_objects as go
import pandas as pd

def create_price_chart(data):
    """
    Create a price chart from data
    """
    if not data:
        return go.Figure()
        
    fig = go.Figure()
    
    # Try to parse DefiLlama or CoinGecko format
    # CoinGecko format: {'prices': [[ts, p], ...]}
    try:
        if isinstance(data, dict):
            if 'prices' in data and isinstance(data['prices'], list):
                # CoinGecko
                df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                fig.add_trace(go.Scatter(x=df['date'], y=df['price'], mode='lines', name='Price'))
            elif 'coins' in data:
                # DefiLlama
                 for key, val in data['coins'].items():
                     prices = val.get('prices', [])
                     if prices:
                         df = pd.DataFrame(prices)
                         df['date'] = pd.to_datetime(df['timestamp'], unit='s')
                         fig.add_trace(go.Scatter(x=df['date'], y=df['price'], mode='lines', name='Price'))
    except:
        pass

    fig.update_layout(title="Price Chart", xaxis_title="Date", yaxis_title="Price")
    return fig

def create_holders_pie_chart(data):
    """
    Create a pie chart for holder distribution (Legacy)
    """
    if not data:
        return go.Figure()
    
    fig = go.Figure()
    fig.update_layout(title="Holders Distribution (Placeholder)")
    return fig

def create_holders_bar_chart(data):
    """
    Create a bar chart for holders, sorted by balance descending
    """
    # Handle wrapped response (e.g. Nansen {"data": [...]})
    if isinstance(data, dict) and 'data' in data:
        data = data['data']

    if not data or not isinstance(data, list):
        return go.Figure()
        
    df = pd.DataFrame(data)
    
    # Check column names. Nansen might use 'balance' or 'tokens_owned' or similar.
    # And 'owner' or 'address_label' or 'address'
    
    balance_col = None
    for c in ['balance', 'tokens_owned', 'ownership_percentage', 'token_amount']:
        if c in df.columns:
            balance_col = c
            break
            
    owner_col = None
    for c in ['owner', 'address_label', 'address']:
        if c in df.columns:
            owner_col = c
            break
            
    if balance_col and owner_col:
        # Sort desc
        df = df.sort_values(balance_col, ascending=True) # Ascending for horizontal bar (top at top)
        df = df.tail(20) # Top 20
        
        fig = go.Figure(go.Bar(
            x=df[balance_col],
            y=df[owner_col],
            orientation='h'
        ))
        fig.update_layout(title="Top Token Holders", xaxis_title=balance_col, yaxis_title="Owner")
        return fig
        
    return None

def create_delta_balance_chart(data):
    """
    Create a delta balance change chart with price overlay
    Expecting Dune API result format
    """
    if not data:
        return go.Figure()
    
    # data is likely {"result": {"rows": [...]}} from Dune
    rows = data.get('result', {}).get('rows', [])
    if not rows:
        return go.Figure()
        
    df = pd.DataFrame(rows)
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    elif 'day' in df.columns:
        df['timestamp'] = pd.to_datetime(df['day'])
        df = df.sort_values('timestamp')
    
    fig = go.Figure()
    
    # Convert numeric columns from string if necessary
    numeric_cols = ['positive_delta', 'negative_delta', 'price']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Positive Delta Bars
    if 'positive_delta' in df.columns:
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['positive_delta'],
            name='Positive Delta',
            marker_color='green',
            yaxis='y'
        ))
    
    # Negative Delta Bars
    if 'negative_delta' in df.columns:
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['negative_delta'],
            name='Negative Delta',
            marker_color='red',
            yaxis='y'
        ))
    
    # Price Line (Secondary Y-Axis)
    if 'price' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            name='Price',
            yaxis='y2',
            line=dict(color='blue')
        ))
    
    fig.update_layout(
        title='Delta Balance Change & Price',
        xaxis_title='Date',
        yaxis=dict(
            title='Balance Change',
            side='right'
        ),
        yaxis2=dict(
            title='Price',
            overlaying='y',
            side='left' # Price on left as requested
        ),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
