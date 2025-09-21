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
    ('@finmcp:fred', 'FRED API documentation (Federal Reserve Economic Data)'),
    ('@finmcp:etherscan', 'Etherscan API documentation (Ethereum blockchain)'),
    ('@finmcp:estat', 'e-Stat API documentation (Japan statistics)'),
    ('@finmcp:imf', 'IMF API documentation (International Monetary Fund)'),
    ('@finmcp:bis', 'BIS API documentation (Bank for International Settlements)'),
    ('@finmcp:worldbank', 'World Bank API documentation'),
    ('@finmcp:docs', 'Claude Code MCP documentation')
]

for uri, desc in resources:
    print(f'  • {uri}')
    print(f'    {desc}')
    print()

print('📝 Example usage:')
print('  • @finmcp:fred - Main FRED documentation')
print('  • @finmcp:fred/series - FRED series endpoints')
print('  • @finmcp:etherscan - Etherscan documentation')
print('  • @finmcp:estat - e-Stat API guide')
print('  • @finmcp:imf - IMF data structure docs')
print('  • @finmcp:bis - BIS API endpoints')
print('  • @finmcp:worldbank - World Bank basics')
print('  • @finmcp:docs - Claude Code MCP documentation')
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