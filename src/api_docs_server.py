#!/usr/bin/env python3
"""
FinMCP - Financial API Documentation MCP Server

A Model Context Protocol server that provides access to live API documentation
for financial and economic data sources to prevent Claude from hallucinating
outdated endpoints or parameters.

Supported APIs:
- FRED (Federal Reserve Economic Data)
- Etherscan (Ethereum blockchain data)
- e-Stat (Japan's official statistics)
- IMF (International Monetary Fund)
- BIS (Bank for International Settlements)
- World Bank (World Bank data)
"""

import logging
import os
import re
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from joblib import Memory
from mcp.server import FastMCP
from mcp.types import Resource

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up caching
cache_dir = "./cache"
os.makedirs(cache_dir, exist_ok=True)
memory = Memory(cache_dir, verbose=0)

# Cache TTL: 1 hour (3600 seconds)
CACHE_TTL = 3600

# Server configuration
PORT = int(os.getenv("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP("FinMCP")

# API base URLs and configurations
API_CONFIGS = {
    "fred": {
        "base_url": "https://fred.stlouisfed.org/docs/api/fred/",
        "special_parsing": True,
        "content_selector": ".api-endpoint, .main-content, .content, main"
    },
    "etherscan": {
        "base_url": "https://docs.etherscan.io/",
        "special_parsing": False,
        "content_selector": ".content, main, .documentation, .api-docs"
    },
    "estat": {
        "base_url": "https://www.e-stat.go.jp/api/api/index.php/en/api-info/",
        "special_parsing": False,
        "content_selector": ".content, main, .api-info, .documentation"
    },
    "imf": {
        "base_url": "https://data.imf.org/en/Resource-Pages/IMF-API/",
        "special_parsing": False,
        "content_selector": ".content, main, .api-documentation, .resource-content"
    },
    "bis": {
        "base_url": "https://stats.bis.org/api-doc/v1/",
        "special_parsing": False,
        "content_selector": ".content, main, .api-doc, .documentation"
    },
    "worldbank": {
        "base_url": "https://documents.worldbank.org/en/publication/documents-reports/api/",
        "special_parsing": False,
        "content_selector": ".content, main, .api-documentation, .publication-content"
    }
}


@memory.cache
def fetch_api_documentation(api_name: str, path: str) -> str:
    """
    Fetch API documentation with caching.
    
    Args:
        api_name: Name of the API (fred, etherscan, etc.)
        path: Path component for the specific documentation
        
    Returns:
        Formatted documentation content or error message
    """
    try:
        config = API_CONFIGS.get(api_name)
        if not config:
            return f"Error: Unknown API '{api_name}'. Supported APIs: {', '.join(API_CONFIGS.keys())}"
        
        # Construct URL based on API-specific rules
        if api_name == "fred" and config["special_parsing"]:
            # FRED special handling: replace / with - and append .html for subpaths
            if path and path != "/":
                # Remove leading/trailing slashes and replace internal slashes with hyphens
                formatted_path = path.strip("/").replace("/", "-")
                url = f"{config['base_url']}{formatted_path}.html"
            else:
                url = config["base_url"]
        else:
            # For other APIs, append path directly
            url = urljoin(config["base_url"], path.lstrip("/"))
        
        logger.info(f"Fetching documentation: {url}")
        
        # Fetch the content
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'FinMCP/1.0 (Financial API Documentation MCP Server)'
        })
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract main content using selectors
        content = None
        selectors = config["content_selector"].split(", ")
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0]
                break
        
        # Fallback to body if no specific content found
        if not content:
            content = soup.find('body') or soup
        
        # Clean up the content
        if content:
            # Remove script and style elements
            for element in content(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get text content
            text_content = content.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            text_content = re.sub(r'\n\s*\n\s*\n', '\n\n', text_content)
            text_content = re.sub(r'[ \t]+', ' ', text_content)
            
            formatted_content = f"""# {api_name.upper()} API Documentation

**Source URL:** {url}
**Fetched:** {response.headers.get('date', 'Unknown')}
**Status:** {response.status_code}

---

{text_content}

---

**Note:** This documentation was fetched live from the official API documentation.
Always verify the latest information at the source URL above.
"""
            logger.info(f"Successfully fetched and parsed documentation for {api_name}: {path}")
            return formatted_content
        else:
            logger.warning(f"No content found for {api_name}: {path}")
            return f"Error: No content could be extracted from {url}"
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching documentation for {api_name} at path '{path}': {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error processing documentation for {api_name} at path '{path}': {str(e)}"
        logger.error(error_msg)
        return error_msg


def get_fred_docs(path: str) -> str:
    """Fetch FRED API documentation."""
    return fetch_api_documentation("fred", path)


def get_etherscan_docs(path: str) -> str:
    """Fetch Etherscan API documentation."""
    return fetch_api_documentation("etherscan", path)


def get_estat_docs(path: str) -> str:
    """Fetch e-Stat API documentation."""
    return fetch_api_documentation("estat", path)


def get_imf_docs(path: str) -> str:
    """Fetch IMF API documentation."""
    return fetch_api_documentation("imf", path)


def get_bis_docs(path: str) -> str:
    """Fetch BIS API documentation."""
    return fetch_api_documentation("bis", path)


def get_worldbank_docs(path: str) -> str:
    """Fetch World Bank API documentation."""
    return fetch_api_documentation("worldbank", path)


# Register MCP resources for each API
@mcp.resource("api-docs://fred/{path}")
async def fred_documentation(path: str) -> Resource:
    """
    Fetch FRED (Federal Reserve Economic Data) API documentation.
    
    Examples:
    - api-docs://fred/ - Main FRED API documentation
    - api-docs://fred/v2/series - Series endpoints documentation
    - api-docs://fred/v2/series/observations - Series observations documentation
    """
    content = get_fred_docs(path)
    return Resource(
        uri=f"api-docs://fred/{path}",
        name=f"FRED API Documentation: {path or 'Main'}",
        description=f"Live FRED API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


@mcp.resource("api-docs://etherscan/{path}")
async def etherscan_documentation(path: str) -> Resource:
    """
    Fetch Etherscan API documentation.
    
    Examples:
    - api-docs://etherscan/ - Main Etherscan API documentation
    - api-docs://etherscan/api-endpoints - API endpoints documentation
    - api-docs://etherscan/getting-started - Getting started guide
    """
    content = get_etherscan_docs(path)
    return Resource(
        uri=f"api-docs://etherscan/{path}",
        name=f"Etherscan API Documentation: {path or 'Main'}",
        description=f"Live Etherscan API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


@mcp.resource("api-docs://estat/{path}")
async def estat_documentation(path: str) -> Resource:
    """
    Fetch e-Stat (Japan's official statistics) API documentation.
    
    Examples:
    - api-docs://estat/ - Main e-Stat API documentation
    - api-docs://estat/api-guide - API guide documentation
    - api-docs://estat/data-format - Data format documentation
    """
    content = get_estat_docs(path)
    return Resource(
        uri=f"api-docs://estat/{path}",
        name=f"e-Stat API Documentation: {path or 'Main'}",
        description=f"Live e-Stat API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


@mcp.resource("api-docs://imf/{path}")
async def imf_documentation(path: str) -> Resource:
    """
    Fetch IMF (International Monetary Fund) API documentation.
    
    Examples:
    - api-docs://imf/ - Main IMF API documentation
    - api-docs://imf/getting-started - Getting started guide
    - api-docs://imf/data-structure - Data structure documentation
    """
    content = get_imf_docs(path)
    return Resource(
        uri=f"api-docs://imf/{path}",
        name=f"IMF API Documentation: {path or 'Main'}",
        description=f"Live IMF API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


@mcp.resource("api-docs://bis/{path}")
async def bis_documentation(path: str) -> Resource:
    """
    Fetch BIS (Bank for International Settlements) API documentation.
    
    Examples:
    - api-docs://bis/ - Main BIS API documentation
    - api-docs://bis/endpoints - API endpoints documentation
    - api-docs://bis/data-sets - Available data sets documentation
    """
    content = get_bis_docs(path)
    return Resource(
        uri=f"api-docs://bis/{path}",
        name=f"BIS API Documentation: {path or 'Main'}",
        description=f"Live BIS API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


@mcp.resource("api-docs://worldbank/{path}")
async def worldbank_documentation(path: str) -> Resource:
    """
    Fetch World Bank API documentation.
    
    Examples:
    - api-docs://worldbank/ - Main World Bank API documentation
    - api-docs://worldbank/basic-call-structure - Basic call structure
    - api-docs://worldbank/data-catalog - Data catalog documentation
    """
    content = get_worldbank_docs(path)
    return Resource(
        uri=f"api-docs://worldbank/{path}",
        name=f"World Bank API Documentation: {path or 'Main'}",
        description=f"Live World Bank API documentation for {path or 'main page'}",
        mimeType="text/plain",
        text=content
    )


def main():
    """Run the MCP server."""
    import sys
    
    # Check if we're running in stdio mode (for VS Code) or HTTP mode
    if "--stdio" in sys.argv or not sys.stdin.isatty():
        # Run in stdio mode for VS Code MCP
        logger.info(f"Starting FinMCP server in stdio mode")
        logger.info(f"Cache directory: {os.path.abspath(cache_dir)}")
        logger.info(f"Supported APIs: {', '.join(API_CONFIGS.keys())}")
        mcp.run(transport="stdio")
    else:
        # Run as HTTP server
        logger.info(f"Starting FinMCP server on http://localhost:{PORT}")
        logger.info(f"Cache directory: {os.path.abspath(cache_dir)}")
        logger.info(f"Supported APIs: {', '.join(API_CONFIGS.keys())}")
        import uvicorn
        uvicorn.run(mcp.sse_app, host="localhost", port=PORT)


if __name__ == "__main__":
    main()