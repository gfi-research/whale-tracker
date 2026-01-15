import ccxt
import time
from collections import defaultdict, deque

class CVDTracker:
    def __init__(self):
        self.trades = deque()
        self.seen_trade_ids = set()
        self.windows = {
            '5m': 5 * 60,
            '1h': 60 * 60,
            '12h': 12 * 60 * 60,
            '24h': 24 * 60 * 60
        }

    def add_trades(self, trade_list):
        now = time.time()
        for t in trade_list:
            t_id = t.get('id') or f"{t['timestamp']}_{t['amount']}_{t['price']}"
            if t_id not in self.seen_trade_ids:
                delta = t['amount'] if t['side'] == 'buy' else -t['amount']
                self.trades.append((t['timestamp'] / 1000, delta))
                self.seen_trade_ids.add(t_id)
        
        cutoff = now - self.windows['24h']
        while self.trades and self.trades[0][0] < cutoff:
            self.trades.popleft()
        
        if len(self.seen_trade_ids) > 2000:
            self.seen_trade_ids = set(list(self.seen_trade_ids)[-1000:])

    def get_cvd(self, window_key):
        if window_key not in self.windows:
            return 0
        now = time.time()
        limit = self.windows[window_key]
        return sum(delta for ts, delta in self.trades if now - ts <= limit)

class OrderbookEngineSync:
    """Synchronous version for Streamlit compatibility."""
    def __init__(self, exchanges_list, symbol, depth=10):
        self.target_exchanges = exchanges_list
        self.symbol = symbol
        self.depth = depth
        self.trackers = {ex: CVDTracker() for ex in exchanges_list}
        self.exchanges = {}
        self.errors = {}

    def init(self):
        self.errors = {}
        for ex_id in self.target_exchanges:
            try:
                exchange_class = getattr(ccxt, ex_id)
                exchange = exchange_class({'enableRateLimit': True})
                exchange.load_markets()
                self.exchanges[ex_id] = exchange
                
                actual_symbol = self._get_actual_symbol(ex_id)
                trades = exchange.fetch_trades(actual_symbol, limit=100)
                self.trackers[ex_id].add_trades(trades)
            except Exception as e:
                print(f"Error initializing {ex_id}: {e}")
                self.errors[ex_id] = str(e)

    def _get_actual_symbol(self, ex_id):
        exchange = self.exchanges.get(ex_id)
        if not exchange: return self.symbol
        if self.symbol in exchange.markets:
            return self.symbol
        base = self.symbol.split('/')[0]
        for s in exchange.markets:
            if s.startswith(base + '/'):
                return s
        return self.symbol

    def fetch_exchange_data(self, ex_id):
        exchange = self.exchanges.get(ex_id)
        if not exchange: return None
        
        try:
            actual_symbol = self._get_actual_symbol(ex_id)
            ob = exchange.fetch_order_book(actual_symbol, limit=self.depth)
            
            trades = exchange.fetch_trades(actual_symbol, limit=50)
            self.trackers[ex_id].add_trades(trades)
            
            bid_vol = sum(b[1] for b in ob['bids'][:self.depth])
            ask_vol = sum(a[1] for a in ob['asks'][:self.depth])
            
            return {
                'id': ex_id,
                'price': trades[-1]['price'] if trades else (ob['bids'][0][0] if ob['bids'] else 0),
                'bids': ob['bids'],
                'asks': ob['asks'],
                'imbalance': bid_vol - ask_vol,
                'cvd_5m': self.trackers[ex_id].get_cvd('5m'),
                'cvd_1h': self.trackers[ex_id].get_cvd('1h'),
                'cvd_12h': self.trackers[ex_id].get_cvd('12h'),
                'cvd_24h': self.trackers[ex_id].get_cvd('24h')
            }
        except Exception as e:
            print(f"Error fetching {ex_id}: {e}")
            return None

    def fetch_all(self):
        results = []
        for ex_id in self.target_exchanges:
            data = self.fetch_exchange_data(ex_id)
            if data:
                results.append(data)
        return results

    def fetch_candle_history(self, timeframe='1m', limit=100):
        # Prefer Binance, then Bybit, then others
        preferred = ['binance', 'bybit', 'coinbase', 'hyperliquid']
        
        for ex_id in preferred:
            if ex_id in self.exchanges:
                try:
                    exchange = self.exchanges[ex_id]
                    actual_symbol = self._get_actual_symbol(ex_id)
                    ohlcv = exchange.fetch_ohlcv(actual_symbol, timeframe, limit=limit)
                    # Format: [[timestamp, open, high, low, close, volume], ...]
                    return {
                        'exchange': ex_id,
                        'data': ohlcv
                    }
                except Exception as e:
                    print(f"Error fetching OHLCV from {ex_id}: {e}")
                    continue
        return None
