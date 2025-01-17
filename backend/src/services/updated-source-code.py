# File: src/api/routes.py

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .middleware import RateLimiter, AuthMiddleware, ErrorHandler
from ..data.meta_analyzer import MetaAnalyzer
from ..data.market_stats import MarketStats
from ..data.database import Database
from ..utils.config import Config
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Pydantic models
class TokenInfo(BaseModel):
    address: str
    name: str
    symbol: str
    price: float
    volume_24h: float
    market_cap: float
    meta_name: Optional[str] = None

class MetaAnalysis(BaseModel):
    name: str
    popularity: float
    trend_direction: str
    sentiment_score: float
    related_tokens: List[str]

class MarketHealth(BaseModel):
    health_score: float
    sentiment_score: float
    risk_score: float
    opportunity_score: float
    timestamp: datetime

# Initialize FastAPI app
app = FastAPI(
    title="Zham API",
    description="Advanced Solana blockchain and social media analytics API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(RateLimiter())
app.middleware("http")(AuthMiddleware())
app.middleware("http")(ErrorHandler())

# Initialize components
db = Database()
meta_analyzer = MetaAnalyzer()
market_stats = MarketStats(db)

@app.get("/api/v1/meta/current", response_model=Dict[str, List[MetaAnalysis]])
async def get_current_meta():
    """Get current meta analysis"""
    try:
        data = await meta_analyzer.analyze_current_meta()
        return data
    except Exception as e:
        logger.error(f"Error in get_current_meta: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch current meta")

# Additional routes remain the same with updated documentation...

# File: src/data/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Meta(Base):
    __tablename__ = 'zham_metas'  # Updated table name
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    popularity = Column(Float)
    trend_direction = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    related_tokens = relationship("Token", back_populates="meta")
    sentiment_score = Column(Float)
    analysis_data = Column(JSON)

class Token(Base):
    __tablename__ = 'zham_tokens'  # Updated table name
    
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True)
    name = Column(String)
    symbol = Column(String)
    meta_id = Column(Integer, ForeignKey('zham_metas.id'))
    meta = relationship("Meta", back_populates="related_tokens")
    price = Column(Float)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    performance_metrics = Column(JSON)

class MarketAnalysis(Base):
    __tablename__ = 'zham_market_analysis'  # Updated table name
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    overall_sentiment = Column(Float)
    market_trends = Column(JSON)
    risk_factors = Column(JSON)
    opportunities = Column(JSON)
    ai_predictions = Column(JSON)

# File: src/api/websocket_providers.py

class DataProvider:
    """Base class for Zham WebSocket data providers"""
    def __init__(self):
        self.solana_client = SolanaClient()
        self.twitter_client = TwitterClient()
        self.meta_analyzer = MetaAnalyzer()
        self.market_stats = MarketStats()
        self.ai_interface = OpenAIInterface()
        self.cache = {}

    async def get_data(self) -> Dict:
        """Get data for broadcast - to be implemented by subclasses"""
        raise NotImplementedError

# Additional DataProvider implementations remain the same...

# File: src/data/meta_analyzer.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import tweepy
import openai
from datetime import datetime, timedelta

@dataclass
class MetaData:
    name: str
    popularity: float
    trend_direction: str
    related_tokens: List[str]
    sentiment_score: float

class MetaAnalyzer:
    """Zham Meta Analyzer for market trends and sentiment analysis"""
    def __init__(self):
        self.db = Database()
        self.solana_client = SolanaClient()
        self.twitter_client = TwitterClient()
        self.ai_interface = OpenAIInterface()
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    async def analyze_current_meta(self) -> Dict[str, List[MetaData]]:
        """Analyze current market meta trends in the Zham ecosystem"""
        try:
            # Implementation remains the same...
            pass
        except Exception as e:
            logger.error(f"Error analyzing current meta: {e}")
            return {
                "top_trending": [],
                "rising": [],
                "declining": []
            }

# Additional method implementations remain the same...