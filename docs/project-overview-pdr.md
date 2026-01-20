# Whale Tracker Dashboard - Project Overview and PDR

## Project Summary

**Project Name:** Whale Tracker Dashboard
**Version:** 0.0.0 (MVP)
**Repository:** `/whale-website`
**Status:** Configuration complete, implementation in progress

### Description

The Whale Tracker Dashboard is a web application designed to track and analyze smart money positions on the Hyperliquid perpetual exchange. It aggregates data from the Nansen API to provide real-time insights into whale wallet activities, helping traders understand market sentiment and large-player positioning.

### Goals

1. **Transparency:** Provide visibility into large wallet positions on Hyperliquid
2. **Market Intelligence:** Enable users to identify smart money trends and positioning
3. **Accessibility:** Present complex trading data in an intuitive, scannable format
4. **Performance:** Deliver fast, responsive data visualization with minimal latency

---

## Target Users

### Primary Users

| User Type | Description | Key Needs |
|-----------|-------------|-----------|
| Retail Traders | Individual traders seeking market insights | Quick access to whale positions, sentiment indicators |
| Analysts | Market researchers studying institutional flows | Detailed position data, historical trends |
| Quant Developers | Algorithmic traders building strategies | Structured data, API-friendly formats |

### Use Cases

1. **Position Monitoring:** Track specific whale wallets and their current positions
2. **Sentiment Analysis:** Gauge overall market sentiment based on aggregate smart money bias
3. **Market Research:** Analyze position distributions across tokens and entity types
4. **Trade Validation:** Cross-reference personal trading decisions with whale activity

---

## Product Development Requirements (PDR)

### Core Features

#### 1. Wallet Table View

**Priority:** P0 (Critical)

| Requirement | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Wallet List | Display all 210 tracked wallets | All wallets render with correct metadata |
| Sortable Columns | Sort by value, ROI, PnL, entity type | Click headers to toggle sort direction |
| Filter by Entity | Filter wallets by retail/VCs/MM | Filter toggles work correctly |
| Filter by Cohort | Filter by size tier (Kraken/Whale/Shark/Fish) | Cohort filters apply immediately |
| Search | Search wallets by address or label | Partial match search works |
| Pagination | Handle large dataset efficiently | Virtual scrolling or pagination |

#### 2. Market Aggregation View

**Priority:** P0 (Critical)

| Requirement | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Token Overview | Show aggregate positions per token | Long/short notional values displayed |
| Sentiment Indicator | Visual representation of market bias | Clear bullish/bearish/neutral styling |
| Trader Count | Number of wallets per token | Accurate count per token |
| PnL Summary | Aggregate unrealized PnL | Profit/loss clearly distinguished |

#### 3. Position Detail Modal

**Priority:** P1 (High)

| Requirement | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Wallet Details | Show full wallet information | Address, label, entity, total value |
| Position List | Individual positions for wallet | Token, direction, size, PnL displayed |
| Position Metrics | Entry price, mark price, leverage | All metrics accurate and formatted |
| Liquidation Price | Show liquidation risk | Highlighted when close to current price |

### Non-Functional Requirements

#### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial Load | < 2 seconds | Time to First Contentful Paint |
| Table Render | < 100ms | Time to render 210 wallet rows |
| Data Refresh | < 500ms | API response + UI update |
| Bundle Size | < 500KB | Gzipped production build |

#### Accessibility

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Keyboard Navigation | WCAG 2.1 AA | Full keyboard support for tables and modals |
| Screen Reader | WCAG 2.1 AA | Proper ARIA labels and landmarks |
| Color Contrast | WCAG 2.1 AA | Minimum 4.5:1 ratio for text |
| Focus Indicators | WCAG 2.1 AA | Visible focus rings on interactive elements |

#### Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

### Success Criteria

| Criterion | Target | Measurement Method |
|-----------|--------|-------------------|
| Page Load Speed | Lighthouse Performance > 90 | Lighthouse audit |
| User Task Completion | Find specific wallet < 10 seconds | User testing |
| Error Rate | < 1% failed API requests | Error monitoring |
| Data Freshness | Cache invalidation at 5 minutes | React Query logs |

---

## API Constraints and Compliance

### Nansen API Integration

#### Allowed Endpoints (No Attribution Required)

| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `/profiler/perp-positions` | Fetch individual wallet positions | Standard |
| `/profiler/address/pnl-summary` | Get wallet PnL summary | Standard |

#### Allowed Endpoints (Attribution Required)

| Endpoint | Purpose | Attribution |
|----------|---------|-------------|
| `/tgm/perp-screener` | Market-wide position aggregation | "Powered by Nansen" badge required |

#### Prohibited Endpoints

| Endpoint | Reason |
|----------|--------|
| `/smart-money/perp-trades` | License restrictions - DO NOT USE |

### Compliance Requirements

1. **Attribution:** Display "Powered by Nansen" when using `/tgm/perp-screener` data
2. **Rate Limiting:** Implement request throttling to respect API limits
3. **Caching:** Use 5-minute cache to reduce API load
4. **Error Handling:** Graceful degradation when API is unavailable

---

## Future Roadmap

### Phase 2: Enhanced Analytics

- Historical position tracking
- Position change alerts
- Portfolio correlation analysis

### Phase 3: User Features

- Wallet watchlists
- Custom filters and views
- Export functionality (CSV/JSON)

### Phase 4: Real-Time Updates

- WebSocket integration for live updates
- Push notifications for significant moves
- Real-time PnL tracking

### Technical Debt Considerations

- Implement comprehensive error boundaries
- Add unit and integration tests
- Set up monitoring and alerting
- Consider SSR for SEO (if needed)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-19 | Technical Writer | Initial documentation |
