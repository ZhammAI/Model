# backend/src/api/routes/twitter.py

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..services.twitter_service import TwitterService

router = APIRouter()
twitter_service = TwitterService()

@router.get("/mentions/{symbol}")
async def get_memecoin_mentions(symbol: str):
    """Get Twitter mentions for a specific memecoin"""
    mentions = await twitter_service.track_memecoin_mentions([symbol])
    if not mentions:
        raise HTTPException(status_code=404, detail="No mentions found")
    return mentions.get(symbol, {})

@router.get("/meta/trends")
async def get_meta_trends():
    """Get current meta trends from Twitter"""
    trends = await twitter_service.analyze_meta_trends()
    if not trends:
        raise HTTPException(status_code=404, detail="No trends found")
    return trends

@router.get("/influencers")
async def get_influencer_activity(usernames: Optional[List[str]] = None):
    """Get crypto influencer activity"""
    if not usernames:
        usernames = ['DegenSpartan', 'solana', 'rothschilds']  # Default influencers
    activity = await twitter_service.get_influencer_activity(usernames)
    if not activity:
        raise HTTPException(status_code=404, detail="No influencer activity found")
    return activity