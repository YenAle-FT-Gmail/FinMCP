"""
Provider Intelligence for FinMCP - Enhanced with AskQuant's intelligent routing.
Adds smart provider recommendations and query classification capabilities.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, date
from .api_docs_server import API_CONFIGS

class QueryClassifier:
    """Classifies financial data queries to extract requirements."""
    
    def __init__(self):
        """Initialize the query classifier with keyword mappings."""
        
        # Data type keywords mapping
        self.data_type_keywords = {
            "stocks": ["stock", "share", "equity", "ticker", "symbol", "price", "volume", "market cap"],
            "options": ["option", "call", "put", "strike", "expiry", "iv", "implied volatility"],
            "crypto": ["crypto", "bitcoin", "btc", "ethereum", "eth", "cryptocurrency", "defi", "nft"],
            "forex": ["forex", "fx", "currency", "exchange rate", "usd", "eur", "gbp", "jpy"],
            "economic_indicators": ["gdp", "growth", "economic", "indicator", "macro"],
            "inflation": ["inflation", "cpi", "consumer price", "pce", "deflator"],
            "employment": ["employment", "unemployment", "jobs", "payroll", "labor", "nfp"],
            "interest_rates": ["interest rate", "fed funds", "libor", "sofr", "yield", "bond", "treasury"],
            "housing": ["housing", "home", "mortgage", "real estate", "construction"],
            "earnings": ["earnings", "revenue", "profit", "eps", "pe ratio", "income"],
            "fundamentals": ["fundamental", "balance sheet", "cash flow", "ratios"],
            "filings": ["filing", "10-k", "10-q", "8-k", "sec", "edgar"],
            "news": ["news", "headline", "article", "sentiment", "mention"],
        }
        
        # Geographic keywords
        self.geographic_keywords = {
            "US": ["us", "usa", "united states", "america", "american", "nasdaq", "nyse", "s&p"],
            "EU": ["eu", "europe", "european", "eurozone", "ecb"],
            "UK": ["uk", "britain", "british", "london", "ftse"],
            "Japan": ["japan", "japanese", "tokyo", "nikkei", "yen"],
            "China": ["china", "chinese", "shanghai", "shenzhen", "yuan", "rmb"],
            "Global": ["global", "world", "international", "worldwide"],
        }
        
        # Preference keywords
        self.preference_keywords = {
            "free": ["free", "no cost", "without paying", "no api key"],
            "fast": ["fast", "quick", "instant", "immediate", "low latency"],
            "comprehensive": ["comprehensive", "complete", "all", "everything", "detailed"],
            "official": ["official", "government", "authoritative", "primary source"],
        }
    
    def classify_query(self, query: str) -> Dict:
        """
        Classify a user query to extract data requirements.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with classified requirements
        """
        query_lower = query.lower()
        
        classification = {
            "original_query": query,
            "data_types": self._extract_data_types(query_lower),
            "geography": self._extract_geography(query_lower),
            "preferences": self._extract_preferences(query_lower),
            "specific_symbols": self._extract_symbols(query),
        }
        
        # Add chain-of-thought reasoning
        classification["reasoning"] = self._generate_reasoning(classification)
        
        return classification
    
    def _extract_data_types(self, query: str) -> List[str]:
        """Extract data types from query."""
        found_types = []
        
        for data_type, keywords in self.data_type_keywords.items():
            if any(keyword in query for keyword in keywords):
                found_types.append(data_type)
        
        return found_types
    
    def _extract_geography(self, query: str) -> List[str]:
        """Extract geographic requirements from query."""
        found_geo = []
        
        for geo, keywords in self.geographic_keywords.items():
            if any(keyword in query for keyword in keywords):
                found_geo.append(geo)
        
        return found_geo if found_geo else ["Global"]
    
    def _extract_preferences(self, query: str) -> List[str]:
        """Extract user preferences from query."""
        found_prefs = []
        
        for pref, keywords in self.preference_keywords.items():
            if any(keyword in query for keyword in keywords):
                found_prefs.append(pref)
        
        return found_prefs
    
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract ticker symbols from query."""
        # Common pattern for tickers (1-5 uppercase letters)
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, query)
        
        # Filter out common words that might match pattern
        common_words = {"US", "UK", "EU", "GDP", "CPI", "API", "REST", "JSON", "CSV"}
        tickers = [t for t in potential_tickers if t not in common_words]
        
        return list(set(tickers))
    
    def _generate_reasoning(self, classification: Dict) -> str:
        """Generate chain-of-thought reasoning for the classification."""
        reasoning_parts = []
        
        # Data type reasoning
        if classification["data_types"]:
            reasoning_parts.append(
                f"User is looking for {', '.join(classification['data_types'])} data"
            )
        else:
            reasoning_parts.append("No specific data type identified, will search broadly")
        
        # Geographic reasoning
        if classification["geography"] != ["Global"]:
            reasoning_parts.append(
                f"Geographic focus: {', '.join(classification['geography'])}"
            )
        
        # Preference reasoning
        if "free" in classification["preferences"]:
            reasoning_parts.append("Prefers free/no API key providers")
        if "fast" in classification["preferences"]:
            reasoning_parts.append("Prefers low-latency providers (local data if available)")
        if "official" in classification["preferences"]:
            reasoning_parts.append("Prefers official/government sources")
        
        return " → ".join(reasoning_parts)

class ProviderMatcher:
    """Matches classified queries to appropriate providers."""
    
    def __init__(self):
        """Initialize the provider matcher."""
        self.providers = API_CONFIGS
    
    def match_providers(self, classification: Dict, top_n: int = 5) -> List[Dict]:
        """
        Match providers based on query classification.
        
        Args:
            classification: Classified query from QueryClassifier
            top_n: Number of top providers to return
            
        Returns:
            List of matched providers with scores
        """
        matches = []
        
        for provider_id, config in self.providers.items():
            score = self._calculate_match_score(classification, config, provider_id)
            
            if score > 0:
                matches.append({
                    "provider": provider_id,
                    "name": config["name"],
                    "score": score,
                    "match_reasons": self._get_match_reasons(classification, config),
                    "requires_key": config.get("requires_api_key", False),
                    "free_tier": config.get("free_tier", False),
                    "local_available": config.get("local_available", False),
                    "response_time": config.get("response_time", "Unknown"),
                })
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        return matches[:top_n]
    
    def _calculate_match_score(self, classification: Dict, config: Dict, provider_id: str) -> float:
        """Calculate match score between query and provider."""
        score = 0.0
        
        # Data type matching (most important)
        provider_types = set(config.get("data_types", []))
        query_types = set(classification["data_types"])
        
        if query_types and provider_types:
            overlap = len(query_types & provider_types)
            if overlap > 0:
                score += overlap * 1.0  # 1 point per matching data type
            else:
                return 0  # No data type match, skip this provider
        elif not query_types:
            # No specific data type requested, give small base score
            score += 0.1
        
        # Geographic matching
        provider_geo = set(config.get("geographic_coverage", []))
        query_geo = set(classification["geography"])
        
        if "Global" in provider_geo or query_geo & provider_geo:
            score += 0.5
        elif not query_geo or "Global" in query_geo:
            score += 0.2  # Partial credit if no specific geography
        
        # Preference matching
        preferences = classification["preferences"]
        
        if "free" in preferences:
            if config.get("free_tier"):
                score += 0.5
            if not config.get("requires_api_key"):
                score += 0.3
        
        if "fast" in preferences:
            if config.get("local_available"):
                score += 1.0  # Strong preference for local data
            response_time = config.get("response_time", "")
            if "ms" in response_time and any(x in response_time for x in ["<100", "<50", "<10"]):
                score += 0.5
        
        if "official" in preferences:
            # Check if it's a government source
            govt_providers = ["fred", "sec", "bls", "treasury", "ecb", "imf", "worldbank", "oecd", "estat"]
            if provider_id in govt_providers:
                score += 0.8
        
        if "comprehensive" in preferences:
            # Prefer providers with many data types
            score += len(config.get("data_types", [])) * 0.05
        
        return max(0, score)  # Don't return negative scores
    
    def _get_match_reasons(self, classification: Dict, config: Dict) -> List[str]:
        """Get human-readable reasons for why provider matches."""
        reasons = []
        
        # Data type matches
        provider_types = set(config.get("data_types", []))
        query_types = set(classification["data_types"])
        matching_types = query_types & provider_types
        
        if matching_types:
            reasons.append(f"Provides {', '.join(matching_types)} data")
        
        # Geographic coverage
        provider_geo = set(config.get("geographic_coverage", []))
        query_geo = set(classification["geography"])
        
        if query_geo & provider_geo:
            reasons.append(f"Covers {', '.join(query_geo & provider_geo)}")
        elif "Global" in provider_geo:
            reasons.append("Global coverage")
        
        # Special features
        if config.get("local_available"):
            reasons.append("Local database available (<10ms)")
        
        if config.get("free_tier"):
            reasons.append("Free tier available")
        elif not config.get("requires_api_key"):
            reasons.append("No API key required")
        
        return reasons

def create_provider_recommendation(query: str) -> str:
    """
    Create a provider recommendation based on a user query.
    
    Args:
        query: User's natural language query
        
    Returns:
        Formatted recommendation with reasoning
    """
    classifier = QueryClassifier()
    matcher = ProviderMatcher()
    
    # Classify the query
    classification = classifier.classify_query(query)
    
    # Match providers
    matches = matcher.match_providers(classification, top_n=5)
    
    # Format the recommendation
    recommendation = f"""# Provider Recommendation for Query

## Query Analysis
**Original Query**: {query}
**Reasoning**: {classification['reasoning']}

## Detected Requirements
- **Data Types**: {', '.join(classification['data_types']) if classification['data_types'] else 'Not specified'}
- **Geography**: {', '.join(classification['geography'])}
- **Preferences**: {', '.join(classification['preferences']) if classification['preferences'] else 'None specified'}

## Recommended Providers
"""
    
    if matches:
        for i, match in enumerate(matches, 1):
            recommendation += f"""
### {i}. {match['name']} ({match['provider']})
- **Score**: {match['score']:.2f}
- **Match Reasons**: {'; '.join(match['match_reasons'])}
- **API Key Required**: {'Yes' if match['requires_key'] else 'No'}
- **Free Tier**: {'Yes' if match['free_tier'] else 'No'}
- **Local Data**: {'Yes' if match['local_available'] else 'No'}
- **Response Time**: {match['response_time']}
"""
    else:
        recommendation += "\nNo matching providers found for this query."
    
    return recommendation