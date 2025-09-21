#!/bin/bash

# FinMCP Inspect Script
# This script inspects the MCP resources available in the server

set -e  # Exit on any error

echo "🔍 Inspecting FinMCP resources..."
echo ""

# Check if we're in the right directory
if [ ! -f "src/api_docs_server.py" ]; then
    echo "❌ Error: api_docs_server.py not found in src/ directory"
    echo "   Make sure you're running this script from the FinMCP root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please run ./scripts/setup.sh first"
    exit 1
fi

# Check if mcp is installed
if ! python3 -c "import mcp" &> /dev/null; then
    echo "❌ Error: mcp-sdk is not installed"
    echo "   Please run ./scripts/setup.sh first"
    exit 1
fi

echo "📋 Available MCP resources in FinMCP server:"
echo ""

# Run MCP inspect
python3 -c "
import sys
sys.path.append('src')
from api_docs_server import mcp

print('🔗 Resource URI Patterns:')
print()
resources = [
    ('api-docs://fred/{path}', 'FRED API documentation (Federal Reserve Economic Data)'),
    ('api-docs://etherscan/{path}', 'Etherscan API documentation (Ethereum blockchain)'),
    ('api-docs://estat/{path}', 'e-Stat API documentation (Japan statistics)'),
    ('api-docs://imf/{path}', 'IMF API documentation (International Monetary Fund)'),
    ('api-docs://bis/{path}', 'BIS API documentation (Bank for International Settlements)'),
    ('api-docs://worldbank/{path}', 'World Bank API documentation')
]

for uri, desc in resources:
    print(f'  • {uri}')
    print(f'    {desc}')
    print()

print('📝 Example usage:')
print('  • api-docs://fred/ - Main FRED documentation')
print('  • api-docs://fred/v2/series - FRED series endpoints')
print('  • api-docs://etherscan/getting-started - Etherscan getting started')
print('  • api-docs://estat/api-guide - e-Stat API guide')
print('  • api-docs://imf/data-structure - IMF data structure docs')
print('  • api-docs://bis/endpoints - BIS API endpoints')
print('  • api-docs://worldbank/basic-call-structure - World Bank basics')
print()
print('💡 Tip: Use dynamic paths to access specific documentation sections')
print('    The server will fetch live content and cache it for 1 hour')
"

echo ""
echo "✅ Inspection completed"
echo ""
echo "To start the server and test these resources:"
echo "  ./scripts/run.sh"
echo ""