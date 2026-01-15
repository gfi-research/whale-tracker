# Hyperliquid Whale Screener Dashboard

A real-time analytics dashboard for tracking and visualizing high-value traders ("whales") on the Hyperliquid decentralized exchange. Monitor portfolio allocations, trading activity patterns, and performance metrics across 116+ whale wallets.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd demo-port

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## Features

### Portfolio Screening
Screen 116+ whale wallets with filters for entity type (VCs, Market Makers, Retail), wallet count, and sorting options. View real-time perp vs spot allocation breakdowns.

### Distribution Analysis
- **Value vs Perp Heatmap** - See how portfolio size correlates with perpetual futures allocation
- **Entity vs Perp Heatmap** - Compare allocation strategies across VCs, MMs, and retail traders
- **Value vs PnL Heatmap** - Analyze profitability across portfolio size segments
- **Statistical Histograms** - Distribution charts for Perp %, Account Value, and PnL

### Activity Calendar
GitHub-style heatmaps showing trading activity over time:
- Single wallet view with detailed trade breakdowns
- All-wallets combined view for market-wide activity patterns
- Color-coded by trade direction (Long = Green, Short = Red)

### Trade Analysis
- Recent trades table (last 100 trades with timestamp, coin, direction, size, price, PnL)
- Activity breakdown by coin (top 10 most traded)
- Activity breakdown by wallet (in all-wallets mode)

---

## Project Structure

```
demo-port/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── wallet_address.txt      # Whale wallet addresses (116 wallets)
├── README.md               # This file
├── docs/                   # Detailed documentation
│   ├── project-overview-pdr.md    # Product requirements
│   ├── codebase-summary.md        # Code overview
│   ├── code-standards.md          # Coding standards
│   └── system-architecture.md     # Architecture docs
└── src/
    ├── api/
    │   └── hyperliquid.py  # Hyperliquid API client
    ├── components/
    │   └── charts.py       # Reusable chart components
    └── utils/
        └── formatters.py   # Number formatting utilities
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >= 1.31.0 | Web application framework |
| plotly | >= 5.18.0 | Interactive visualizations |
| pandas | >= 2.0.0 | Data manipulation |
| requests | >= 2.31.0 | HTTP client for API |
| python-dotenv | >= 1.0.0 | Environment configuration |

---

## Configuration

### Wallet Data

The application loads whale wallet addresses from `wallet_address.txt`, a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `trader_address_label` | Human-readable wallet name |
| `Entity` | Category: VCs, MM, or retail |
| `trader_address` | Ethereum address (0x...) |
| `account_value` | Account value from CSV |
| `roi` | Return on investment |
| `total_pnl(unrealize profit)` | Unrealized PnL |

### Time Periods

Supported time periods for portfolio analysis:
- **Day** - Last 24 hours
- **Week** - Last 7 days
- **Month** - Last 30 days
- **All Time** - Complete history

---

## Usage

### Basic Workflow

1. **Initial Load** - Application displays CSV-based wallet list
2. **Apply Filters** - Use sidebar to filter by entity type, wallet count, sort order
3. **Fetch Live Data** - Click "Fetch Live Data" to get real-time portfolio breakdowns
4. **Explore Charts** - View stacked bar charts, heatmaps, and histograms
5. **Activity Analysis** - Select wallet(s) and year range, click "Fetch Activity"

### Keyboard Shortcuts

- `R` - Rerun the application
- `C` - Clear cache and rerun

---

## API Reference

The dashboard integrates with the Hyperliquid Info API:

| Endpoint | Purpose |
|----------|---------|
| `type: portfolio` | Fetch user portfolio data |
| `type: userFills` | Fetch recent trade fills |
| `type: userFillsByTime` | Fetch trades within date range |

API Base URL: `https://api.hyperliquid.xyz/info`

---

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Perp | `#3bb5d3` | Perpetual futures allocation |
| Spot | `#7dd3fc` | Spot trading allocation |
| Background | `#1a2845` | Main background |
| Positive/Long | `#22c55e` | Profit, long positions |
| Negative/Short | `#e74c3c` | Loss, short positions |

---

## Documentation

For detailed documentation, see the `/docs` directory:

- **[Product Requirements](docs/project-overview-pdr.md)** - Feature specifications and roadmap
- **[Codebase Summary](docs/codebase-summary.md)** - File descriptions and data flow
- **[Code Standards](docs/code-standards.md)** - Naming conventions and styling
- **[System Architecture](docs/system-architecture.md)** - Component diagrams and integrations

---

## Tracked Entities

| Entity Type | Examples | Count |
|-------------|----------|-------|
| **VCs** | Fasanara Capital, Abraxas Capital, Galaxy Digital, Selini | ~10 |
| **Market Makers** | Wintermute | ~5 |
| **Retail** | Smart traders, trading bots, whales | ~100 |

---

## Troubleshooting

### Common Issues

**"Could not load wallet addresses"**
- Ensure `wallet_address.txt` exists in the project root
- Check CSV format matches expected columns

**No data fetched after clicking button**
- Check internet connection
- Hyperliquid API may be rate limiting; wait and retry
- Verify wallet addresses are valid Ethereum addresses

**Charts not rendering**
- Ensure Plotly is installed: `pip install plotly>=5.18.0`
- Check browser console for JavaScript errors

### Performance Tips

- Reduce "Number of Wallets" slider for faster fetches
- Use shorter time periods (Day/Week) for quicker responses
- Activity calendar fetches can take 2+ minutes for all wallets

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Follow code standards in `docs/code-standards.md`
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- [Hyperliquid](https://hyperliquid.xyz) - DEX and API provider
- [Streamlit](https://streamlit.io) - Application framework
- [Plotly](https://plotly.com) - Visualization library
