"""
Super RAG - Cognitive Operating System
Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Super RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Redis - Working Memory
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DEFAULT_TTL: int = 3600  # 1 hour
    REDIS_MAX_MEMORY: str = "1gb"
    
    # Milvus - Semantic Memory
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "semantic_memory"
    MILVUS_INDEX_TYPE: str = "IVF_FLAT"
    MILVUS_NLIST: int = 1024
    MILVUS_QUANTIZATION: str = "RaBitQ"
    MILVUS_MAX_MEMORY: str = "2gb"
    
    # PostgreSQL - Episodic Memory
    POSTGRES_URI: str = "postgresql://user:password@localhost:5432/episodic_memory"
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 10
    
    # Neo4j - Knowledge Graph
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_MAX_HEAP: str = "512m"
    NEO4J_PAGE_CACHE: str = "256m"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    EMBEDDING_DIMENSION: int = 4096
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"
    
    # Chunking Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Model Routing
    MODEL_SIMPLE: str = "google/gemini-2.0-flash-lite"
    MODEL_COMPLEX: str = "google/gemini-2.5-flash"
    MODEL_PREMIUM: str = "anthropic/claude-sonnet-4.5"
    MODEL_RAG: str = "qwen/qwen-2.5-72b-instruct"
    
    # Cost Limits (USD)
    DAILY_COST_LIMIT: float = 10.0
    MONTHLY_COST_LIMIT: float = 200.0
    
    # Search Configuration
    TAVILY_API_KEY: Optional[str] = None
    SEARCH_TOP_K: int = 50
    SEARCH_RERANK_TOP_K: int = 10
    SEMANTIC_THRESHOLD: float = 0.7
    KEYWORD_WEIGHT: float = 0.3
    SEMANTIC_WEIGHT: float = 0.5
    GRAPH_WEIGHT: float = 0.2
    
    # Cache Configuration
    CACHE_TTL: int = 604800  # 7 days
    CACHE_SIMILARITY_THRESHOLD: float = 0.95
    CACHE_MAX_SIZE: int = 10000
    
    # Web Scraping (Playwright)
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1280
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 720
    PLAYWRIGHT_TIMEOUT: int = 30000  # 30 seconds
    PLAYWRIGHT_MAX_CONCURRENT: int = 2
    PLAYWRIGHT_DISABLE_IMAGES: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_USER: int = 100  # requests per hour
    RATE_LIMIT_PER_IP: int = 1000  # requests per hour
    RATE_LIMIT_GLOBAL: int = 10000  # requests per hour
    
    # Circuit Breaker
    CIRCUIT_FAILURE_THRESHOLD: int = 5
    CIRCUIT_RECOVERY_TIMEOUT: int = 60  # seconds
    CIRCUIT_HALF_OPEN_REQUESTS: int = 3
    
    # Freshness
    FRESHNESS_THRESHOLD_DAYS: int = 7
    AUTO_UPDATE_ENABLED: bool = True
    
    # Memory Weights for Fusion
    MEMORY_WEIGHT_SEMANTIC: float = 0.4
    MEMORY_WEIGHT_GRAPH: float = 0.3
    MEMORY_WEIGHT_EPISODIC: float = 0.2
    MEMORY_WEIGHT_INTUITIVE: float = 0.1
    
    # Performance
    MAX_CONCURRENT_QUERIES: int = 20
    QUERY_TIMEOUT: int = 60  # seconds
    MEMORY_QUERY_TIMEOUT: int = 3  # seconds per memory layer
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    OPENTELEMETRY_ENABLED: bool = True
    OPENTELEMETRY_EXPORT_ENDPOINT: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance"""
    return settings
