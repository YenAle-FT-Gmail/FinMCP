#!/bin/bash

# FinMCP Setup Script
# This script installs all required dependencies for the FinMCP server

set -e  # Exit on any error

echo "🚀 Setting up FinMCP (Financial API Documentation MCP Server)..."
echo ""

# Check if Python 3.8+ is available
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.8 or later and try again"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Found Python $python_version"

# Check if Python version is 3.8 or later
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python version is compatible (3.8+)"
else
    echo "❌ Error: Python 3.8 or later is required"
    echo "   Current version: $python_version"
    exit 1
fi

# Check if pip is available
echo ""
echo "📦 Checking pip availability..."
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ Error: pip is not available"
    echo "   Please install pip and try again"
    exit 1
fi
echo "✅ pip is available"

# Install dependencies
echo ""
echo "📥 Installing Python dependencies from requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "   Make sure you're running this script from the FinMCP root directory"
    exit 1
fi

python3 -m pip install -r requirements.txt

echo ""
echo "📁 Creating cache directory..."
mkdir -p cache
echo "✅ Cache directory created"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run the server: ./scripts/run.sh"
echo "2. Inspect MCP resources: ./scripts/inspect.sh"
echo "3. Integrate with Claude (see README.md for details)"
echo ""