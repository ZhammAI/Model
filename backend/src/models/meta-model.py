# backend/src/models/meta.py

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class MetaPerformance(BaseModel):
    volume_24h: float = Field(..., description="24h trading volume")
    volume_change: float = Field(..., description="Volume change percentage")
    token_count: int = Field(..., description="Number of tokens")
    average_roi: float = Field(..., description="Average ROI of tokens")
    winning_tokens: int = Field(..., description="Number of tokens with positive ROI")

class MetaToken(BaseModel):
    address: str
    name: str
    symbol: str
    price_change_24h: float
    volume_24h: float
    market_cap: float
    score: float = Field(..., description="Token's relevance score for this meta")

class MetaMomentum(BaseModel):
    score: float = Field(..., description="Momentum score (-100 to 100)")
    trend: str = Field(..., description="Current trend direction")
    strength: str = Field(..., description="Trend strength")
    velocity: float = Field(..., description="Rate of change")

class MetaSocialMetrics(BaseModel):
    mentions_24h: int
    sentiment_score: float
    trending_platforms: List[str]
    influencer_mentions: int
    engagement_rate: float

class MetaHistoricalData(BaseModel):
    timestamp: datetime
    percentage: float
    volume: float
    token_count: int
    average_roi: Optional[float]

class MetaTrend(BaseModel):
    name: str = Field(..., description="Meta trend name")
    percentage: float = Field(..., description="Current trend percentage")
    momentum: MetaMomentum
    performance: MetaPerformance
    social_metrics: MetaSocialMetrics
    top_tokens: List[MetaToken] = Field(default_list=[])

class MetaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: List[str]
    category: Optional[str] = None

class MetaUpdate(BaseModel):
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class Meta(BaseModel):
    id: int
    name: str
    description: Optional[str]
    keywords: List[str]
    category: Optional[str]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    trend_data: Optional[MetaTrend] = None
    historical_data: List[MetaHistoricalData] = Field(default_list=[])

    class Config:
        from_attributes = True

# Response Models
class MetaResponse(BaseModel):
    success: bool = Field(default=True)
    data: Meta
    message: Optional[str] = None

class MetaTrendsResponse(BaseModel):
    success: bool = Field(default=True)
    data: Dict[str, List[MetaTrend]] = Field(
        ...,
        description="Categorized trends (trending, rising, declining)"
    )
    timestamp: datetime
    message: Optional[str] = None

class MetaAnalysis(BaseModel):
    correlation_matrix: Dict[str, Dict[str, float]]
    cluster_analysis: List[Dict[str, List[str]]]
    trend_predictions: Dict[str, Dict[str, float]]
    market_impact: Dict[str, float]

# Request Models
class MetaFilterParams(BaseModel):
    min_volume: Optional[float] = None
    min_token_count: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = True
    time_range: Optional[str] = "24h"
    sort_by: Optional[str] = "percentage"
    sort_desc: bool = True

class MetaMomentumParams(BaseModel):
    volume_weight: float = Field(default=0.3, ge=0, le=1)
    social_weight: float = Field(default=0.3, ge=0, le=1)
    performance_weight: float = Field(default=0.4, ge=0, le=1)
    time_window: str = Field(default="24h")

class MetaCorrelationParams(BaseModel):
    metas: List[str]
    time_range: str = "7d"
    metrics: List[str] = ["volume", "price", "social"]

# Custom Types
class MetaCategory(BaseModel):
    name: str
    description: str
    active_metas: int
    total_volume_24h: float
    average_momentum: float

class MetaPrediction(BaseModel):
    meta_name: str
    prediction: str
    confidence: float
    factors: List[Dict[str, float]]
    timeframe: str
    generated_at: datetime

class MetaAlert(BaseModel):
    meta_name: str
    alert_type: str
    severity: str
    message: str
    metrics: dict
    timestamp: datetime