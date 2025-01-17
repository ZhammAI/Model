# backend/src/services/token_service.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from solana.rpc.async_api import AsyncClient
import logging

class TokenService:
    def __init__(self):
        self.solana_client = AsyncClient("https://api.mainnet-beta.solana.com")
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_expiry = 300  # 5 minutes

    async def get_token_info(self, address: str) -> Dict:
        """Get detailed token information"""
        try:
            # Check cache first
            if self._cache.get(address) and \
               self._cache[address]['timestamp'] > datetime.now() - timedelta(seconds=self._cache_expiry):
                return self._cache[address]['data']

            # Fetch token data from Solana
            token_account = await self.solana_client.get_account_info(address)
            
            # Get additional data from other sources (Jupiter, Birdeye, etc.)
            price_data = await self._get_price_data(address)
            holder_data = await self._get_holder_data(address)
            social_data = await self._get_social_data(address)

            token_info = {
                "address": address,
                "price": price_data.get("price", 0),
                "price_change_24h": price_data.get("price_change_24h", 0),
                "volume_24h": price_data.get("volume_24h", 0),
                "market_cap": price_data.get("market_cap", 0),
                "holders": holder_data.get("count", 0),
                "liquidity": price_data.get("liquidity", {}),
                "social_metrics": social_data
            }

            # Cache the result
            self._cache[address] = {
                'data': token_info,
                'timestamp': datetime.now()
            }

            return token_info

        except Exception as e:
            self.logger.error(f"Error fetching token info for {address}: {str(e)}")
            raise

    async def get_runners(self, min_volume: Optional[float] = None) -> Dict[str, List]:
        """Get current and potential runners"""
        try:
            # Fetch active tokens
            active_tokens = await self._get_active_tokens()

            # Analyze tokens for runner potential
            current_runners = []
            potential_runners = []

            for token in active_tokens:
                score = await self._calculate_runner_score(token)
                if score > 80:
                    current_runners.append({
                        **token,
                        "score": score
                    })
                elif score > 60:
                    potential_runners.append({
                        **token,
                        "score": score
                    })

            # Filter by volume if specified
            if min_volume:
                current_runners = [r for r in current_runners if r["volume_24h"] >= min_volume]
                potential_runners = [r for r in potential_runners if r["volume_24h"] >= min_volume]

            return {
                "current": sorted(current_runners, key=lambda x: x["score"], reverse=True),
                "potential": sorted(potential_runners, key=lambda x: x["score"], reverse=True)
            }

        except Exception as e:
            self.logger.error(f"Error getting runners: {str(e)}")
            raise

    async def _calculate_runner_score(self, token: Dict) -> float:
        """Calculate a token's runner score based on various metrics"""
        try:
            # Fetch additional metrics
            volume_score = min(100, (token.get("volume_24h", 0) / 10000) * 20)
            price_score = min(100, abs(token.get("price_change_24h", 0)) * 2)
            
            # Get holder metrics
            holder_data = await self._get_holder_data(token["address"])
            holder_score = min(100, (holder_data.get("count", 0) / 1000) * 20)
            
            # Get social metrics
            social_data = await self._get_social_data(token["address"])
            social_score = min(100, (social_data.get("mentions", 0) / 100) * 20)

            # Weighted average
            weights = {
                "volume": 0.3,
                "price": 0.25,
                "holders": 0.25,
                "social": 0.2
            }

            final_score = (
                volume_score * weights["volume"] +
                price_score * weights["price"] +
                holder_score * weights["holders"] +
                social_score * weights["social"]
            )

            return round(final_score, 2)

        except Exception as e:
            self.logger.error(f"Error calculating runner score: {str(e)}")
            return 0

    async def _get_active_tokens(self) -> List[Dict]:
        """Get list of active tokens"""
        try:
            # Implement token discovery logic here
            # For example, query Jupiter API for active pairs
            return []  # Replace with actual implementation
        except Exception as e:
            self.logger.error(f"Error fetching active tokens: {str(e)}")
            return []

    async def _get_price_data(self, address: str) -> Dict:
        """Get token price data"""
        try:
            # Implement price fetching logic here
            # Query Jupiter/Birdeye API
            return {}  # Replace with actual implementation
        except Exception as e:
            self.logger.error(f"Error fetching price data: {str(e)}")
            return {}

    async def _get_holder_data(self, address: str) -> Dict:
        """Get token holder data"""
        try:
            # Implement holder data fetching logic
            return {}  # Replace with actual implementation
        except Exception as e:
            self.logger.error(f"Error fetching holder data: {str(e)}")
            return {}

    async def _get_social_data(self, address: str) -> Dict:
        """Get token social metrics"""
        try:
            # Implement social data fetching logic
            return {}  # Replace with actual implementation
        except Exception as e:
            self.logger.error(f"Error fetching social data: {str(e)}")
            return {}