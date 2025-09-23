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
from provider_intelligence import (
    QueryClassifier,
    ProviderMatcher, 
    create_provider_recommendation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("finmcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List all available API documentation resources."""
    resources = []
    
    # Add resources for each provider
    for api_name, config in API_CONFIGS.items():
        # Main documentation resource
        resources.append(Resource(
            uri=f"finmcp://{api_name}",
            name=f"{config['name']} Documentation",
            description=f"Live {config['name']} API documentation",
            mimeType="text/plain"
        ))
        
        # Add sub-resources for specific doc sections
        for path_name, path in config.get("docs_paths", {}).items():
            if path_name != "main":
                resources.append(Resource(
                    uri=f"finmcp://{api_name}/{path_name}",
                    name=f"{config['name']} - {path_name.replace('_', ' ').title()}",
                    description=f"{config['name']} {path_name} documentation",
                    mimeType="text/plain"
                ))
    
    # Add special resources for intelligent provider discovery
    resources.append(Resource(
        uri="finmcp://providers/list",
        name="All Providers List",
        description="List of all available data providers with capabilities",
        mimeType="text/plain"
    ))
    
    resources.append(Resource(
        uri="finmcp://providers/free",
        name="Free Tier Providers",
        description="Providers with free tier access",
        mimeType="text/plain"
    ))
    
    resources.append(Resource(
        uri="finmcp://providers/local",
        name="Local Database Providers",
        description="Providers with data in local database",
        mimeType="text/plain"
    ))
    
    resources.append(Resource(
        uri="finmcp://intelligence/recommend",
        name="Smart Provider Recommendations",
        description="Get intelligent provider recommendations based on your query",
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
    
    # Handle special provider listing resources
    if api_name == "providers":
        return handle_provider_queries(path)
    
    # Handle intelligent recommendations
    if api_name == "intelligence":
        return handle_intelligence_queries(path)
    
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

def handle_provider_queries(query_type: str) -> str:
    """Handle special provider query resources."""
    
    if query_type == "list":
        # List all providers with enhanced metadata
        providers = []
        for provider_id, config in API_CONFIGS.items():
            data_types = ', '.join(config.get('data_types', [])[:3])
            if len(config.get('data_types', [])) > 3:
                data_types += f" and {len(config['data_types']) - 3} more"
            
            key_req = "API key required" if config.get("requires_api_key") else "No API key"
            free = "Free tier" if config.get("free_tier") else "Paid only"
            local = "Local DB" if config.get("local_available") else "API only"
            
            providers.append(
                f"- **{provider_id}**: {config['name']} "
                f"({data_types}) - {key_req}, {free}, {local}"
            )
        
        return f"""# All Available Providers

{chr(10).join(providers)}

**Total**: {len(providers)} providers supporting 40+ data types
**Free providers**: {sum(1 for v in API_CONFIGS.values() if v.get('free_tier'))}
**Local database**: {sum(1 for v in API_CONFIGS.values() if v.get('local_available'))} providers

Use `finmcp://intelligence/recommend` for smart provider suggestions based on your query.
"""
    
    elif query_type == "free":
        # List free tier providers
        free_providers = []
        for provider_id, config in API_CONFIGS.items():
            if config.get("free_tier"):
                key_req = "API key required" if config.get("requires_api_key") else "No API key"
                rate_limit = config.get("rate_limit", "No limit")
                free_providers.append(
                    f"- **{provider_id}**: {config['name']} ({key_req}) - {rate_limit}"
                )
        
        return f"""# Free Tier Providers

{chr(10).join(free_providers)}

**Total**: {len(free_providers)} providers with free tier access
"""
    
    elif query_type == "local":
        # List providers with local database
        local_providers = []
        for provider_id, config in API_CONFIGS.items():
            if config.get("local_available"):
                response_time = config.get('response_time', 'Fast')
                local_providers.append(
                    f"- **{provider_id}**: {config['name']} - {response_time}"
                )
        
        return f"""# Providers with Local Database

These providers have data pre-loaded for instant access:

{chr(10).join(local_providers) if local_providers else 'No providers currently have local data'}

**Benefits**: <10ms response time, no API key required, no rate limits
"""
    
    else:
        return f"Unknown provider query: {query_type}. Available queries: list, free, local"

def handle_intelligence_queries(query_type: str) -> str:
    """Handle intelligent provider recommendation queries."""
    
    if query_type == "recommend":
        return """# Smart Provider Recommendations

To get intelligent provider recommendations, include your data query in the resource path:

**Examples:**
- `finmcp://intelligence/recommend/US CPI data from 1990`
- `finmcp://intelligence/recommend/real-time Bitcoin prices`
- `finmcp://intelligence/recommend/Japanese unemployment rate`
- `finmcp://intelligence/recommend/free European interest rates`

The system will analyze your query and recommend the best providers based on:
- Data type matching (stocks, crypto, economic indicators, etc.)
- Geographic coverage (US, EU, Japan, Global)
- User preferences (free, fast, official sources)
- Provider capabilities (API keys, rate limits, response time)

**Query Classification Process:**
1. Extract data types from natural language
2. Identify geographic requirements
3. Detect user preferences (free, fast, official)
4. Score providers based on match quality
5. Return top 5 recommendations with reasoning
"""
    
    else:
        # Treat the query_type as the actual query to analyze
        query = query_type.replace('/', ' ')  # Convert URL path back to query
        return create_provider_recommendation(query)

async def main():
    """Run the MCP server."""
    logger.info("Starting Enhanced FinMCP server in stdio mode")
    logger.info(f"Supported APIs: {len(API_CONFIGS)} providers")
    logger.info("Enhanced with intelligent provider routing and recommendations")
    
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