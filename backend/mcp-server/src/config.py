"""
NYC POI Concierge MCP Server - Configuration
MongoDB x Tavily x LastMile AI Hackathon
"""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class MongoDBConfig(BaseModel):
    """MongoDB Atlas configuration"""
    uri: str = os.getenv("MONGODB_URI", "")
    database: str = os.getenv("MONGODB_DATABASE", "nyc-poi")
    pois_collection: str = os.getenv("MONGODB_POIS_COLLECTION", "pois")
    # Timeouts and connection settings
    max_pool_size: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "10"))
    server_selection_timeout_ms: int = int(os.getenv("MONGODB_TIMEOUT", "5000"))
    
    def __post_init__(self):
        if not self.uri:
            raise ValueError("MONGODB_URI environment variable is required")


class TavilyConfig(BaseModel):
    """Tavily API configuration"""
    api_key: str = os.getenv("TAVILY_API_KEY", "")
    search_depth: str = os.getenv("TAVILY_SEARCH_DEPTH", "advanced")
    max_results: int = int(os.getenv("TAVILY_MAX_RESULTS", "10"))
    include_raw_content: bool = os.getenv("TAVILY_INCLUDE_RAW", "true").lower() == "true"
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")


class OpenAIConfig(BaseModel):
    """OpenAI API configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimensions: int = int(os.getenv("OPENAI_EMBEDDING_DIMS", "1536"))
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")


class WeatherConfig(BaseModel):
    """OpenWeatherMap API configuration"""
    api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    units: str = os.getenv("OPENWEATHER_UNITS", "imperial")  # Fahrenheit for NYC
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")


class PerplexityConfig(BaseModel):
    """Perplexity Sonar API configuration"""
    api_key: str = os.getenv("PERPLEXITY_API_KEY", "")
    model: str = os.getenv("PERPLEXITY_MODEL", "sonar")  # "sonar" or "sonar-pro"
    search_recency_filter: str = os.getenv("PERPLEXITY_RECENCY", "month")  # month, week, day
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")


class MCPConfig(BaseModel):
    """MCP Server configuration"""
    server_name: str = os.getenv("MCP_SERVER_NAME", "nyc-poi-concierge")
    server_version: str = os.getenv("MCP_SERVER_VERSION", "0.1.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


class AppConfig:
    """Main application configuration"""
    
    def __init__(self):
        self.mongodb = MongoDBConfig()
        self.tavily = TavilyConfig()
        self.openai = OpenAIConfig()
        self.weather = WeatherConfig()
        self.perplexity = PerplexityConfig()
        self.mcp = MCPConfig()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENV", "development") == "production"
    
    @property
    def use_mock_data(self) -> bool:
        """Check if using mock data (for parallel development)"""
        return os.getenv("USE_MOCK_DATA", "false").lower() == "true"


# Global config instance
config = AppConfig()
