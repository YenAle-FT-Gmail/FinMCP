# Enhanced FinMCP - Financial Data Provider Intelligence

Enhanced Model Context Protocol server providing intelligent access to 40+ financial data providers with smart routing and recommendations.

## Features

### 🎯 Intelligent Provider Routing
- **Query Classification**: Understands natural language queries to extract data requirements
- **Smart Matching**: Scores providers based on data type, geography, preferences, and capabilities  
- **Chain-of-Thought**: Provides reasoning for why providers were recommended
- **40+ Providers**: Government sources (FRED, SEC, ECB) + Commercial APIs (Polygon, Alpha Vantage, etc.)

### 📊 Provider Categories
- **Government Data (60%)**: Free tier, official sources, some with local databases
- **Commercial APIs (40%)**: API keys required, comprehensive coverage, real-time data

### ⚡ Performance Optimization
- **Local Database**: Instant <10ms responses for government data
- **Free Tier Priority**: Automatically recommends free options when available
- **Rate Limit Awareness**: Considers API limits in recommendations

## Quick Start

### 1. Installation
```bash
git clone <this-repo>
cd FinMCP
pip install -r requirements.txt
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "finmcp": {
      "command": "python",
      "args": ["/path/to/FinMCP/src/mcp_server.py"]
    }
  }
}
```

### 3. Usage Examples

#### Provider Discovery
- `@finmcp:finmcp://providers/list` - All 40+ providers
- `@finmcp:finmcp://providers/free` - Free tier providers only  
- `@finmcp:finmcp://providers/local` - Local database providers

#### Smart Recommendations
- `@finmcp:finmcp://intelligence/recommend/US CPI data from 1990`
- `@finmcp:finmcp://intelligence/recommend/real-time Bitcoin prices`
- `@finmcp:finmcp://intelligence/recommend/free European interest rates`

#### Live Documentation
- `@finmcp:finmcp://fred` - FRED API documentation
- `@finmcp:finmcp://polygon/stocks` - Polygon stocks documentation
- `@finmcp:finmcp://coingecko` - CoinGecko crypto documentation

## Intelligence System

### Query Classification
The system automatically extracts:
- **Data Types**: stocks, crypto, economic_indicators, inflation, etc.
- **Geography**: US, EU, Japan, Global coverage requirements
- **Preferences**: free, fast, official sources, comprehensive data
- **Symbols**: Ticker symbols (AAPL, BTC) and time requirements

### Provider Scoring
Providers are scored based on:
1. **Data Type Match** (1.0 points per match)
2. **Geographic Coverage** (0.5 points)
3. **User Preferences** (0.3-1.0 points)
4. **Special Features** (local data, free tier, official source)

### Example: "US CPI data from 1990"
```
Classification:
- Data Types: inflation
- Geography: US
- Preferences: None

Top Recommendations:
1. FRED (Score: 2.3) - Local database, official source
2. BLS (Score: 1.8) - Government source, comprehensive
```

## Supported Providers

### Government Sources (Free/Official)
- **FRED**: Federal Reserve Economic Data
- **SEC**: SEC EDGAR filings  
- **BLS**: Bureau of Labor Statistics
- **ECB**: European Central Bank
- **IMF**: International Monetary Fund
- **World Bank**: Development data
- **OECD**: International statistics
- **Treasury**: US Treasury data
- **e-Stat**: Japan official statistics

### Commercial APIs
- **Polygon.io**: Real-time market data
- **Alpha Vantage**: Stocks, forex, crypto
- **Twelve Data**: Global market data
- **CoinGecko**: Cryptocurrency data
- **Yahoo Finance**: Global market data (free)
- **Financial Modeling Prep**: Fundamentals
- **Tiingo**: News and market data
- **Finnhub**: Market data and news
- **IEX Cloud**: US market data
- **Quandl**: Alternative data

## Development

### Adding New Providers
1. Add configuration to `API_CONFIGS` in `api_docs_server.py`
2. Include: name, base_url, data_types, geographic_coverage, etc.
3. Test with validation script

### Provider Configuration
```python
"provider_id": {
    "name": "Provider Name",
    "base_url": "https://api.provider.com/docs",
    "data_types": ["stocks", "crypto"],
    "geographic_coverage": ["US", "Global"],
    "requires_api_key": True,
    "free_tier": True,
    "local_available": False,
    "response_time": "~100ms"
}
```

## Architecture

```
Claude Query → MCP Resource → Query Classifier → Provider Matcher → Live Docs
     ↓              ↓              ↓                ↓               ↓
"Bitcoin price" → intelligence → [crypto,Global] → CoinGecko → API docs
```

## Use Cases

### Financial Research
- **Academic**: Free government data with historical coverage
- **Trading**: Real-time market data with low latency
- **Analysis**: Comprehensive fundamental data

### Development
- **API Discovery**: Find the right provider for your data needs
- **Cost Optimization**: Prefer free tiers and local databases
- **Geographic Compliance**: Match data sources to regulatory requirements

## Contributing

1. Fork the repository
2. Add new providers to `API_CONFIGS`
3. Test intelligent routing
4. Submit pull request

## License

MIT License - See LICENSE file for details.

---

**Enhanced FinMCP** transforms Claude into an intelligent financial data assistant that knows about 40+ providers and can route queries optimally based on requirements, cost, and performance.