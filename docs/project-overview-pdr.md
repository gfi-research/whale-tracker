# Hyperliquid Whale Screener Dashboard - Product Development Requirements

**Document Version:** 1.0
**Last Updated:** January 2026
**Status:** Production

---

## Executive Summary

The Hyperliquid Whale Screener Dashboard is a real-time analytics platform designed to track, analyze, and visualize trading patterns of high-value traders ("whales") on the Hyperliquid decentralized exchange. The application provides comprehensive portfolio breakdowns, distribution analysis, and GitHub-style activity tracking for 116+ whale wallets with combined assets under management exceeding $700M.

This tool enables cryptocurrency traders, analysts, and researchers to gain actionable insights into whale behavior, identify market trends, and understand portfolio allocation strategies across perpetual futures (perp) and spot trading markets.

---

## Problem Statement

### Market Challenge

Tracking whale behavior on decentralized exchanges presents significant challenges:

1. **Data Fragmentation** - Blockchain data requires aggregation from multiple sources and complex API interactions
2. **No Centralized Dashboards** - Existing tools focus on single-wallet analysis rather than cohort screening
3. **Limited Visual Analytics** - Raw blockchain data lacks intuitive visualization for pattern recognition
4. **Time-Intensive Research** - Manual wallet monitoring is inefficient for tracking multiple addresses
5. **Missing Historical Context** - Point-in-time snapshots fail to reveal trading patterns over time

### Solution Approach

The Whale Screener Dashboard addresses these challenges by providing:

- Batch fetching of portfolio data across 100+ wallets
- Comparative visualization of perp vs spot allocations
- Distribution heatmaps revealing market positioning clusters
- Activity calendars showing long/short trade patterns over time
- Real-time integration with Hyperliquid's Info API

---

## Target Users

### Primary Users

| User Type | Description | Key Needs |
|-----------|-------------|-----------|
| **Crypto Traders** | Active traders seeking alpha from whale movements | Real-time data, trade signals, activity patterns |
| **Market Analysts** | Research professionals studying market dynamics | Distribution analysis, entity comparisons, PnL tracking |
| **Fund Managers** | Portfolio managers tracking competitors | AUM breakdowns, allocation strategies, risk metrics |
| **DeFi Researchers** | Academics studying DEX behavior | Historical data, statistical distributions, entity categorization |

### Secondary Users

- **Risk Managers** - Monitoring exposure and leverage patterns
- **Journalists** - Researching stories on whale activity
- **Protocol Teams** - Understanding user behavior on Hyperliquid

---

## Core Features

### 1. Portfolio Screening and Filtering

**Capability:** Screen all whale wallets with configurable filters

| Filter | Options | Purpose |
|--------|---------|---------|
| Entity Type | All, VCs, MM, Retail | Segment by trader category |
| Wallet Count | 10 - 116 (slider) | Control data volume |
| Sort By | Account Value, Perp %, PnL | Prioritize analysis focus |
| Time Period | Day, Week, Month, All Time | Temporal analysis scope |

### 2. Stacked Bar Charts

**Capability:** Visualize perp vs spot allocation across all wallets

- **Value Mode:** Absolute dollar amounts for size comparison
- **Percentage Mode:** 100% stacked bars for allocation comparison
- Supports Account Value, PnL, and Volume metrics
- Color-coded: Perp (#3bb5d3), Spot (#7dd3fc)

### 3. Distribution Heatmaps

**Capability:** Reveal clustering patterns in whale portfolios

| Heatmap | X-Axis | Y-Axis | Cell Value |
|---------|--------|--------|------------|
| Value vs Perp | Account Value bins | Perp % bins | Wallet count |
| Entity vs Perp | Entity type | Perp % bins | Total AUM |
| Value vs PnL | Account Value bins | PnL bins | Wallet count |

### 4. Statistical Histograms

**Capability:** Distribution analysis for key metrics

- Perp % distribution (10 bins)
- Account Value distribution (15 bins)
- PnL distribution (20 bins)

### 5. Activity Calendar

**Capability:** GitHub-style heatmap showing trading activity over time

| Trade Type | Color | Indicator |
|------------|-------|-----------|
| Open Long | Green | Bullish entry |
| Close Long | Blue | Taking profits |
| Open Short | Red | Bearish entry |
| Close Short | Orange | Covering shorts |

**Features:**
- Single wallet view with date range selection
- All-wallets combined heatmap
- Individual wallet expandable sections
- Hover details showing dominant trade type

### 6. Trade Analysis Tables

**Capability:** Detailed trade-level data exploration

- Recent 100 trades with timestamp, coin, direction, size, price, PnL, fee
- Activity by Coin aggregation (top 10)
- Activity by Wallet aggregation (multi-wallet mode)

---

## Technical Requirements

### Frontend Requirements

| Requirement | Specification |
|-------------|---------------|
| Framework | Streamlit >= 1.31.0 |
| Charting | Plotly >= 5.18.0 |
| Layout | Wide mode with sidebar |
| Theme | Dark mode (#1a2845 background) |
| Responsiveness | Full-width charts with dynamic heights |

### Backend Requirements

| Requirement | Specification |
|-------------|---------------|
| Language | Python 3.8+ |
| Data Processing | pandas >= 2.0.0 |
| HTTP Client | requests >= 2.31.0 |
| Environment | python-dotenv >= 1.0.0 |

### External Integrations

| Integration | Endpoint | Purpose |
|-------------|----------|---------|
| Hyperliquid Info API | `https://api.hyperliquid.xyz/info` | Portfolio and trade data |

**API Endpoints Used:**

- `type: portfolio` - Fetch user portfolio data
- `type: userFills` - Fetch recent trade fills
- `type: userFillsByTime` - Fetch trades within date range

### Data Requirements

| Data Source | Format | Records |
|-------------|--------|---------|
| Wallet Addresses | CSV | 116 wallets |
| Entity Categories | VCs, MM, Retail | 3 categories |
| Historical Trades | JSON from API | Variable per wallet |

---

## Performance Requirements

| Metric | Target | Notes |
|--------|--------|-------|
| Initial Load | < 2 seconds | CSV parsing only |
| Data Fetch (single) | < 1 second | Per wallet API call |
| Data Fetch (all) | < 120 seconds | 116 wallets with rate limiting |
| Chart Render | < 500ms | After data loaded |
| Memory Usage | < 500MB | With full dataset loaded |

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Wallet Coverage | 100+ wallets | Tracked addresses |
| Data Freshness | Real-time | API fetch on demand |
| Chart Load Time | < 1 second | Post-data render |
| Entity Coverage | 3 categories | VCs, MM, Retail |

### Qualitative Metrics

- Users can identify whale positioning trends within 5 minutes
- Distribution patterns are immediately apparent from heatmaps
- Activity calendars reveal trading frequency patterns at a glance
- Trade tables provide drill-down capability for detailed analysis

---

## Future Roadmap

### Phase 2: Enhanced Analytics

- [ ] Real-time WebSocket updates for live trade streaming
- [ ] Customizable alerts for whale activity thresholds
- [ ] Position size change tracking over time
- [ ] Liquidation risk assessment metrics

### Phase 3: Advanced Features

- [ ] Machine learning classification of trading strategies
- [ ] Cross-wallet correlation analysis
- [ ] Social sentiment integration
- [ ] Export functionality (CSV, PDF reports)

### Phase 4: Platform Expansion

- [ ] Multi-DEX support (dYdX, GMX, etc.)
- [ ] User authentication and saved preferences
- [ ] API access for programmatic queries
- [ ] Mobile-responsive design

---

## Constraints and Assumptions

### Constraints

1. **API Rate Limits** - Hyperliquid API may throttle requests; 50ms delays implemented between calls
2. **Data Availability** - Historical data limited by API retention policies
3. **Wallet Identification** - Entity labels are manually curated and may require updates
4. **Browser Dependency** - Streamlit requires modern browser support

### Assumptions

1. Wallet addresses in CSV remain valid and active
2. Hyperliquid API maintains backward compatibility
3. Users have stable internet connections for API fetching
4. Entity categorization accurately reflects trader types

---

## Glossary

| Term | Definition |
|------|------------|
| **Perp** | Perpetual futures contracts with no expiration date |
| **Spot** | Direct asset purchases/sales without leverage |
| **AUM** | Assets Under Management - total portfolio value |
| **PnL** | Profit and Loss - realized trading gains/losses |
| **Whale** | High-value trader, typically >$1M in portfolio value |
| **MM** | Market Maker - professional liquidity provider |
| **VC** | Venture Capital - institutional investment fund |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | January 2026 | Development Team | Initial release |
