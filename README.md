# FinMCP - Financial API Documentation MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Prevent Claude from hallucinating outdated API endpoints!** FinMCP provides live access to official API documentation for major financial and economic data sources.

## 🎯 Purpose

FinMCP is a Model Context Protocol (MCP) server that fetches **live API documentation** from official sources, ensuring Claude always has access to the most current endpoint information, parameters, and usage examples. No more outdated API calls or hallucinated endpoints!

## 🏦 Supported APIs

| API | Base URL | Description |
|-----|----------|-------------|
| **FRED** | https://fred.stlouisfed.org/docs/api/fred/ | Federal Reserve Economic Data |
| **Etherscan** | https://docs.etherscan.io/ | Ethereum blockchain data |
| **e-Stat** | https://www.e-stat.go.jp/api/api/index.php/en/api-info/ | Japan's official statistics |
| **IMF** | https://data.imf.org/en/Resource-Pages/IMF-API/ | International Monetary Fund |
| **BIS** | https://stats.bis.org/api-doc/v1/ | Bank for International Settlements |
| **World Bank** | https://documents.worldbank.org/en/publication/documents-reports/api/ | World Bank data |

## ✨ Features

- **🔴 Live Documentation Fetching**: Always up-to-date information directly from official sources
- **📂 Dynamic Path Support**: Access specific documentation sections (e.g., `v2/series/observations`)
- **⚡ Smart Caching**: 1-hour cache with joblib to avoid rate limits and improve performance
- **🧹 Content Parsing**: BeautifulSoup extraction with API-specific selectors for clean content
- **📝 Comprehensive Logging**: Full visibility into fetches, caches, and errors
- **🔧 Easy Integration**: Works with VS Code, Claude Desktop, and terminal API calls
- **🏗️ Modular Architecture**: Easy to extend with additional APIs

## 📋 Prerequisites

- **Python 3.8+**
- **Internet connection** (for fetching live documentation)
- **Claude API access** (for integration)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/FinMCP.git
cd FinMCP

# Run the setup script
./scripts/setup.sh
```

### 2. Start the Server

```bash
# Start the MCP server
./scripts/run.sh
```

The server will start on `http://localhost:8000` by default.

### 3. Inspect Available Resources

```bash
# View all available MCP resources
./scripts/inspect.sh
```

## 🔧 Usage with Claude

### Option 1: VS Code Extension

1. **Install the Anthropic Claude extension** for VS Code
2. **Configure MCP servers** in your settings:

```json
{
  "claude.mcpServers": {
    "finmcp": {
      "url": "http://localhost:8000"
    }
  }
}
```

3. **Use in Claude chat**:

```
@finmcp Please use the latest FRED API documentation to write Python code that fetches unemployment rate data. Use these specific resources:

- api-docs://fred/ (for main API overview)
- api-docs://fred/v2/series/observations (for series data endpoints)

Strictly adhere to the current API documentation. Do not use any endpoints or parameters not explicitly documented in these resources.
```

### Option 2: Terminal API Calls

```bash
# Example: Get FRED API documentation
curl -X POST http://localhost:8000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "method": "resources/read",
    "params": {
      "uri": "api-docs://fred/v2/series/observations"
    }
  }'
```

### Option 3: Claude Desktop Integration

1. **Install MCP support** in Claude Desktop
2. **Add FinMCP server**:

```bash
mcp install src/api_docs_server.py
```

3. **Use in Claude Desktop**:

```
I need to fetch cryptocurrency data from Etherscan. Please reference these resources first:

- api-docs://etherscan/ (main documentation)
- api-docs://etherscan/api-endpoints (available endpoints)

Use ONLY the endpoints and parameters documented in these resources. Do not hallucinate any API calls.
```

## 💡 Sample Prompts for Claude

### Comprehensive Financial Data Analysis

```
I'm building a financial dashboard and need to integrate multiple data sources. Please help me write Python code using the latest official API documentation.

First, fetch and review these documentation resources:
- api-docs://fred/ (Federal Reserve data)
- api-docs://fred/v2/series (FRED series endpoints)
- api-docs://worldbank/ (World Bank API overview)
- api-docs://worldbank/basic-call-structure (World Bank API structure)
- api-docs://imf/ (IMF API documentation)

Requirements:
1. Use ONLY endpoints and parameters explicitly documented in these resources
2. Do NOT hallucinate any API endpoints or parameters
3. Handle API keys and authentication as specified in the documentation
4. Include error handling for API rate limits and network issues
5. Add proper data validation and type hints

Tasks:
1. Fetch US unemployment rate from FRED for the last 12 months
2. Get World Bank GDP data for major economies (US, China, Germany, Japan)
3. Retrieve IMF exchange rate data for USD/EUR/JPY

Provide complete, production-ready Python code with proper documentation.
```

### Blockchain Data Integration

```
Help me integrate Etherscan API for cryptocurrency analysis. Reference these resources:

- api-docs://etherscan/ (main API documentation)
- api-docs://etherscan/getting-started (getting started guide)
- api-docs://etherscan/api-endpoints (complete endpoint list)

Create Python code to:
1. Get the latest block information
2. Fetch transaction details for a specific address
3. Retrieve ERC-20 token balance for an address

Use ONLY the documented endpoints and follow the exact parameter names and formats shown in the documentation. Include proper error handling and rate limiting.
```

### International Economic Data

```
I need to compare economic indicators across different countries using official APIs. Please reference:

- api-docs://estat/ (Japan e-Stat API)
- api-docs://estat/api-guide (e-Stat usage guide)
- api-docs://bis/ (Bank for International Settlements)
- api-docs://bis/data-sets (available BIS datasets)

Create code to fetch:
1. Japan's inflation rate from e-Stat
2. International banking statistics from BIS
3. Cross-country economic comparisons

Ensure all API calls follow the exact specifications in the documentation.
```

## 📖 API Resource Examples

### FRED (Federal Reserve Economic Data)

```
api-docs://fred/                           # Main FRED API documentation
api-docs://fred/v2/series                  # Series endpoints
api-docs://fred/v2/series/observations     # Series observations (time series data)
api-docs://fred/v2/releases                # Economic data releases
api-docs://fred/v2/sources                 # Data sources information
```

### Etherscan (Ethereum Blockchain)

```
api-docs://etherscan/                      # Main Etherscan API docs
api-docs://etherscan/getting-started       # Getting started guide
api-docs://etherscan/api-endpoints         # Complete API endpoint list
api-docs://etherscan/rate-limits           # Rate limiting information
```

### e-Stat (Japan Statistics)

```
api-docs://estat/                          # Main e-Stat API documentation
api-docs://estat/api-guide                 # API usage guide
api-docs://estat/data-format               # Data format specifications
api-docs://estat/statistical-data          # Available statistical datasets
```

### IMF (International Monetary Fund)

```
api-docs://imf/                           # Main IMF API documentation
api-docs://imf/getting-started            # Getting started with IMF API
api-docs://imf/data-structure             # Data structure and formats
api-docs://imf/country-codes              # Country code mappings
```

### BIS (Bank for International Settlements)

```
api-docs://bis/                           # Main BIS API documentation
api-docs://bis/endpoints                  # Available API endpoints
api-docs://bis/data-sets                  # Available datasets
api-docs://bis/metadata                   # Metadata information
```

### World Bank

```
api-docs://worldbank/                     # Main World Bank API docs
api-docs://worldbank/basic-call-structure # Basic API call structure
api-docs://worldbank/data-catalog         # Data catalog and indicators
api-docs://worldbank/country-queries      # Country-specific queries
```

## 🔧 Configuration

### Environment Variables

- `PORT`: Server port (default: 8000)

```bash
export PORT=8080
./scripts/run.sh
```

### Cache Configuration

- **Cache Location**: `./cache` directory
- **Cache TTL**: 3600 seconds (1 hour)
- **Cache Size**: 100 entries maximum

### Logging

Logs are written to console with INFO level by default. Key information includes:

- API documentation fetches
- Cache hits/misses
- Parsing errors
- Network timeouts

## 🛠️ Development

### Project Structure

```
FinMCP/
├── src/
│   └── api_docs_server.py     # Main MCP server implementation
├── scripts/
│   ├── setup.sh              # Dependency installation
│   ├── run.sh                # Server startup
│   └── inspect.sh            # Resource inspection
├── cache/                    # Auto-created cache directory
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
└── .gitignore               # Git ignore rules
```

### Adding New APIs

1. **Add API configuration** to `API_CONFIGS` in `src/api_docs_server.py`:

```python
"newapi": {
    "base_url": "https://api.example.com/docs/",
    "special_parsing": False,
    "content_selector": ".content, main, .api-docs"
}
```

2. **Create resource handler**:

```python
@mcp.resource("api-docs://newapi/{path:path}")
async def newapi_documentation(path: str) -> Resource:
    content = fetch_api_documentation("newapi", path)
    return Resource(
        uri=f"api-docs://newapi/{path}",
        name=f"NewAPI Documentation: {path or 'Main'}",
        description=f"Live NewAPI documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )
```

3. **Update documentation** in README.md

### Testing

```bash
# Test setup
./scripts/setup.sh

# Test server startup
./scripts/run.sh &
sleep 5

# Test resource inspection
./scripts/inspect.sh

# Test API fetch (example)
curl -X POST http://localhost:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"method": "resources/read", "params": {"uri": "api-docs://fred/"}}'

# Stop server
pkill -f api_docs_server.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Reinstall dependencies
   ./scripts/setup.sh
   ```

2. **Network timeouts**
   - Check internet connection
   - Some APIs may have rate limits
   - Cache will serve previous responses

3. **Permission denied on scripts**
   ```bash
   chmod +x scripts/*.sh
   ```

4. **Port already in use**
   ```bash
   export PORT=8080
   ./scripts/run.sh
   ```

### Debug Mode

Enable detailed logging:

```python
# In src/api_docs_server.py, change:
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-api`
3. **Make your changes** with proper documentation
4. **Add tests** if applicable
5. **Submit a pull request**

### Issues and Feature Requests

- **Bug reports**: Use GitHub Issues with detailed reproduction steps
- **Feature requests**: Propose new APIs or functionality improvements
- **Documentation**: Help improve examples and guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for the Model Context Protocol
- **Federal Reserve Bank of St. Louis** for FRED API
- **Etherscan** for Ethereum data access
- **Statistics Bureau of Japan** for e-Stat API
- **International Monetary Fund** for economic data
- **Bank for International Settlements** for banking statistics
- **World Bank** for development data

---

**Built with ❤️ for the financial data community**

*Last updated: September 21, 2025*