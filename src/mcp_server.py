#!/usr/bin/env python3
"""
FinMCP - Working MCP Server Implementation
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent

from api_docs_server import (
    fetch_api_documentation,
    API_CONFIGS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("finmcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List all available API documentation resources."""
    resources = []
    
    for api_name in API_CONFIGS.keys():
        # Main documentation resource
        resources.append(Resource(
            uri=f"finmcp://{api_name}",
            name=f"{api_name.upper()} API Documentation",
            description=f"Live {api_name.upper()} API documentation from FinMCP server",
            mimeType="text/plain"
        ))
        
    # Add Claude Code MCP documentation
    resources.append(Resource(
        uri="finmcp://docs",
        name="Claude MCP Docs",
        description="Official Claude Code MCP documentation",
        mimeType="text/plain"
    ))
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific API documentation resource."""
    # Convert AnyUrl to string if needed
    uri_str = str(uri)
    
    if not uri_str.startswith("finmcp://"):
        raise ValueError(f"Invalid URI format: {uri_str}")
    
    # Parse URI: finmcp://api_name/path
    uri_parts = uri_str[9:].split("/", 1)  # Remove "finmcp://"
    api_name = uri_parts[0]
    path = uri_parts[1] if len(uri_parts) > 1 else ""
    
    # Handle Claude MCP docs
    if api_name == "docs":
        try:
            response = requests.get("https://docs.claude.com/en/docs/claude-code/mcp", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find('main') or soup.find('body') or soup
            if content:
                for element in content(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                text_content = content.get_text(separator='\n', strip=True)
                return f"# Claude Code MCP Documentation\n\n{text_content}"
            else:
                return "Error: Could not extract Claude MCP documentation"
        except Exception as e:
            return f"Error fetching Claude MCP docs: {str(e)}"
    
    if api_name not in API_CONFIGS:
        raise ValueError(f"Unknown API: {api_name}")
    
    # Fetch the documentation
    try:
        content = fetch_api_documentation(api_name, path)
        return content
    except Exception as e:
        logger.error(f"Error fetching {api_name} docs: {e}")
        return f"Error fetching documentation: {str(e)}"

async def main():
    """Run the MCP server."""
    logger.info("Starting FinMCP server in stdio mode")
    logger.info(f"Supported APIs: {', '.join(API_CONFIGS.keys())}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="finmcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())