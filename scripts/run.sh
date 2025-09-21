#!/bin/bash

# FinMCP Run Script
# This script starts the FinMCP server

set -e  # Exit on any error

echo "🚀 Starting FinMCP (Financial API Documentation MCP Server)..."
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

# Check if dependencies are installed
echo "📋 Checking dependencies..."
if ! python3 -c "import mcp, requests, bs4, joblib" &> /dev/null; then
    echo "❌ Error: Required dependencies are not installed"
    echo "   Please run ./scripts/setup.sh first"
    exit 1
fi
echo "✅ Dependencies are installed"

# Set default port if not specified
export PORT=${PORT:-8000}

echo ""
echo "🌐 Starting server on http://localhost:$PORT"
echo "📁 Cache directory: ./cache"
echo ""
echo "Supported APIs:"
echo "  • FRED (Federal Reserve Economic Data)"
echo "  • Etherscan (Ethereum blockchain data)"
echo "  • e-Stat (Japan's official statistics)"
echo "  • IMF (International Monetary Fund)"
echo "  • BIS (Bank for International Settlements)"
echo "  • World Bank (World Bank data)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 src/api_docs_server.py