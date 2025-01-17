# backend/src/services/meta_service.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict

class MetaService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_expiry = 300  # 5 minutes
        self._meta_history = defaultdict(list)
        self._known_metas = set([
            "ai", "defi", "gaming", "meme", "nft",
            "metaverse", "web3", "dao", "play2earn", "gamefi"
        ])

    async def get_meta_trends(self) -> Dict:
        """Get current meta trends"""
        try:
            cache_key = 'meta_trends'
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']

            # Analyze token names and descriptions
            token_data = await self._fetch_token_data()
            meta_counts = await self._analyze_meta_occurrences(token_data)
            
            # Analyze volumes and performance
            meta_volumes = await self._analyze_meta_volumes(token_data)
            
            # Calculate trend scores
            trends = await self._calculate_trend_scores(meta_counts, meta_volumes)
            
            # Categorize trends
            categorized = self._categorize_trends(trends)
            
            # Update history
            self._update_meta_history(trends)
            
            # Cache results
            self._cache[cache_key] = {
                'data': categorized,
                'timestamp': datetime.now()
            }
            
            return categorized

        except Exception as e:
            self.logger.error(f"Error getting meta trends: {str(e)}")
            raise

    async def get_meta_details(self, meta_name: str) -> Dict:
        """Get detailed information about a specific meta"""
        try:
            if meta_name not in self._known_metas:
                raise ValueError(f"Unknown meta: {meta_name}")

            cache_key = f'meta_details_{meta_name}'
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']

            # Get token data for this meta
            token_data = await self._fetch_token_data(meta_filter=meta_name)
            
            # Calculate metrics
            total_volume = sum(token['volume_24h'] for token in token_data)
            avg_performance = sum(token['price_change_24h'] for token in token_data) / len(token_data) if token_data else 0
            
            # Get historical performance
            history = self._meta_history.get(meta_name, [])
            
            details = {
                'name': meta_name,
                'token_count': len(token_data),
                'total_volume_24h': total_volume,
                'average_performance': avg_performance,
                'trending_score': await self._calculate_meta_score(meta_name),
                'history': history[-30:],  # Last 30 data points
                'top_tokens': sorted(token_data, key=lambda x: x['volume_24h'], reverse=True)[:10]
            }

            # Cache results
            self._cache[cache_key] = {
                'data': details,
                'timestamp': datetime.now()
            }

            return details

        except Exception as e:
            self.logger.error(f"Error getting meta details for {meta_name}: {str(e)}")
            raise

    async def _analyze_meta_occurrences(self, token_data: List[Dict]) -> Dict[str, int]:
        """Analyze meta occurrences in token data"""
        try:
            occurrences = defaultdict(int)
            
            for token in token_data:
                text = f"{token['name']} {token.get('description', '')}".lower()
                for meta in self._known_metas:
                    if meta in text:
                        occurrences[meta] += 1

            return occurrences

        except Exception as e:
            self.logger.error(f"Error analyzing meta occurrences: {str(e)}")
            return defaultdict(int)

    async def _analyze_meta_volumes(self, token_data: List[Dict]) -> Dict[str, float]:
        """Analyze trading volumes for each meta"""
        try:
            volumes = defaultdict(float)
            
            for token in token_data:
                text = f"{token['name']} {token.get('description', '')}".lower()
                volume = token.get('volume_24h', 0)
                
                for meta in self._known_metas:
                    if meta in text:
                        volumes[meta] += volume

            return volumes

        except Exception as e:
            self.logger.error(f"Error analyzing meta volumes: {str(e)}")
            return defaultdict(float)

    async def _calculate_trend_scores(self, counts: Dict[str, int], volumes: Dict[str, float]) -> List[Dict]:
        """Calculate trend scores for metas"""
        try:
            scores = []
            total_volume = sum(volumes.values()) or 1  # Avoid division by zero
            
            for meta in self._known_metas:
                if counts[meta] > 0:
                    volume_percentage = (volumes[meta] / total_volume) * 100
                    momentum = self._calculate_momentum(meta)
                    score = {
                        'name': meta,
                        'percentage': round(volume_percentage, 2),
                        'count': counts[meta],
                        'volume_24h': volumes[meta],
                        'momentum': momentum
                    }
                    scores.append(score)

            return sorted(scores, key=lambda x: x['percentage'], reverse=True)

        except Exception as e:
            self.logger.error(f"Error calculating trend scores: {str(e)}")
            return []

    def _categorize_trends(self, trends: List[Dict]) -> Dict:
        """Categorize trends into trending, rising, and declining"""
        try:
            return {
                'trending': [t for t in trends if t['percentage'] >= 10][:5],
                'rising': [t for t in trends if 5 <= t['percentage'] < 10][:4],
                'declining': [t for t in trends if t['momentum'] < 0][:4]
            }

        except Exception as e:
            self.logger.error(f"Error categorizing trends: {str(e)}")
            return {'trending': [], 'rising': [], 'declining': []}

    def _calculate_momentum(self, meta_name: str) -> float:
        """Calculate momentum for a meta trend"""
        try:
            history = self._meta_history.get(meta_name, [])
            if len(history) < 2:
                return 0

            recent = history[-1]['percentage']
            previous = history[-2]['percentage']
            return round(recent - previous, 2)

        except Exception as e:
            self.logger.error(f"Error calculating momentum: {str(e)}")
            return 0

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key in self._cache:
            age = datetime.now() - self._cache[key]['timestamp']
            return age.seconds < self._cache_expiry
        return False

    def _update_meta_history(self, trends: List[Dict]):
        """Update historical data for meta trends"""
        try:
            timestamp = datetime.now()
            for trend in trends:
                self._meta_history[trend['name']].append({
                    'timestamp': timestamp,
                    'percentage': trend['percentage'],
                    'volume': trend['volume_24h']
                })

                # Keep only last 7 days of history
                cutoff = timestamp - timedelta(days=7)
                self._meta_history[trend['name']] = [
                    h for h in self._meta_history[trend['name']]
                    if h['timestamp'] > cutoff
                ]

        except Exception as e:
            self.logger.error(f"Error updating meta history: {str(e)}")

    async def _fetch_token_data(self, meta_filter: Optional[str] = None) -> List[Dict]:
        """Fetch token data, optionally filtered by meta"""
        try:
            # Implement token data fetching logic here
            # This should query your data source (e.g., database, API)
            return []  # Replace with actual implementation
        except Exception as e:
            self.logger.error(f"Error fetching token data: {str(e)}")
            return []