# backend/src/models/token.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class TokenBase(BaseModel):
    address: str = Field(..., description="Token's Solana address")
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    decimals: int = Field(default=9, description="Token decimals")

class TokenPrice(BaseModel):
    price: float = Field(..., description="Current price in USD")
    price_change_24h: float = Field(..., description="24h price change percentage")
    volume_24h: float = Field(..., description="24h trading volume in USD")
    market_cap: float = Field(..., description="Market capitalization in USD")

class TokenLiquidity(BaseModel):
    usd: float = Field(..., description="Liquidity in USD")
    sol: float = Field(..., description="Liquidity in SOL")
    pair_count: int = Field(default=0, description="Number of trading pairs")

class SocialMetrics(BaseModel):
    twitter_followers: int = Field(default=0)
    telegram_members: int = Field(default=0)
    sentiment_score: float = Field(default=50.0)
    mentions_24h: int = Field(default=0)

class ContractMetrics(BaseModel):
    is_mintable: bool = Field(default=False)
    owner_balance_percentage: float = Field(...)
    renounced_ownership: bool = Field(default=False)
    holder_count: int = Field(...)
    top_holders: List[dict] = Field(default_list=[])

class TokenStats(BaseModel):
    created_at: datetime = Field(...)
    last_traded_at: datetime = Field(...)
    is_verified: bool = Field(default=False)
    meta_tags: List[str] = Field(default_list=[])
    runner_score: Optional[float] = Field(default=None)

class Token(TokenBase):
    price_data: TokenPrice
    liquidity: TokenLiquidity
    social_metrics: SocialMetrics
    contract_metrics: ContractMetrics
    stats: TokenStats

    class Config:
        from_attributes = True

class TokenCreate(TokenBase):
    pass

class TokenUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    price_data: Optional[TokenPrice] = None
    liquidity: Optional[TokenLiquidity] = None
    social_metrics: Optional[SocialMetrics] = None
    contract_metrics: Optional[ContractMetrics] = None
    stats: Optional[TokenStats] = None

class TokenInDB(Token):
    id: int
    created_at: datetime
    updated_at: datetime

# Response Models
class TokenResponse(BaseModel):
    success: bool = Field(default=True)
    data: Token
    message: Optional[str] = None

class TokenListResponse(BaseModel):
    success: bool = Field(default=True)
    data: List[Token]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None
    message: Optional[str] = None

# Request Models
class TokenFilterParams(BaseModel):
    min_volume: Optional[float] = None
    min_liquidity: Optional[float] = None
    min_holders: Optional[int] = None
    meta_tags: Optional[List[str]] = None
    is_verified: Optional[bool] = None
    sort_by: Optional[str] = "volume_24h"
    sort_desc: bool = True
    page: int = 1
    page_size: int = 50

class RunnerScoreParams(BaseModel):
    volume_weight: float = Field(default=0.3, ge=0, le=1)
    price_weight: float = Field(default=0.25, ge=0, le=1)
    holders_weight: float = Field(default=0.25, ge=0, le=1)
    social_weight: float = Field(default=0.2, ge=0, le=1)

class TokenValidation(BaseModel):
    is_valid: bool
    score: float
    warnings: List[str]
    metrics: dict