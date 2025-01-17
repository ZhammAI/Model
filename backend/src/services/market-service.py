# backend/src/services/market_service.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict

class MarketService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_expiry = 300  # 5 minutes
        self._sentiment_history = []
        self._market_metrics = {
            'price_action': 0,
            'volume': 0,
            'social_sentiment': 0,
            'meta_momentum': 0,
            'liquidity_flow': 0
        }

    async def get_market_sentiment(self) -> Dict:
        """Get current market sentiment analysis"""
        try:
            cache_key = 'market_sentiment'
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']

            # Update market metrics
            await self._update_market_metrics()
            
            # Calculate overall sentiment
            sentiment = await self._calculate_sentiment()
            
            # Get sentiment classification
            classification = self._classify_sentiment(sentiment)
            
            result = {
                'value': sentiment,
                'classification': classification,
                'metrics': self._market_metrics,
                'timestamp': datetime.now().isoformat(),
                'trend': self._analyze_sentiment_trend()
            }

            # Update history
            self._update_sentiment_history(result)
            
            # Cache results
            self._cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }

            return result

        except Exception as e:
            self.logger.error(f"Error getting market sentiment: {str(e)}")
            raise

    async def get_market_metrics(self) -> Dict:
        """Get detailed market metrics"""
        try:
            # Get volume metrics
            volume_data = await self._get_volume_metrics()
            
            # Get liquidity metrics
            liquidity_data = await self._get_liquidity_metrics()
            
            # Get social metrics
            social_data = await self._get_social_metrics()

            return {
                'volume_metrics': volume_data,
                'liquidity_metrics': liquidity_data,
                'social_metrics': social_data,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting market metrics: {str(e)}")
            raise

    async def get_market_alerts(self) -> List[Dict]:
        """Get current market alerts"""
        try:
            alerts = []
            
            # Check for significant sentiment changes
            sentiment_change = await self._check_sentiment_change()
            if sentiment_change['is_significant']:
                alerts.append({
                    'type': 'sentiment_shift',
                    'severity': sentiment_change['severity'],
                    'message': sentiment_change['message'],
                    'timestamp': datetime.now().isoformat()
                })

            # Check for volume anomalies
            volume_alerts = await self._check_volume_anomalies()
            alerts.extend(volume_alerts)

            # Check for liquidity changes
            liquidity_alerts = await self._check_liquidity_changes()
            alerts.extend(liquidity_alerts)

            return alerts

        except Exception as e:
            self.logger.error(f"Error getting market alerts: {str(e)}")
            return []

    async def _update_market_metrics(self):
        """Update all market metrics"""
        try:
            # Update price action score
            self._market_metrics['price_action'] = await self._calculate_price_action()
            
            # Update volume score
            self._market_metrics['volume'] = await self._calculate_volume_score()
            
            # Update social sentiment
            self._market_metrics['social_sentiment'] = await self._calculate_social_score()
            
            # Update meta momentum
            self._market_metrics['meta_momentum'] = await self._calculate_meta_momentum()
            
            # Update liquidity flow
            self._market_metrics['liquidity_flow'] = await self._calculate_liquidity_flow()

        except Exception as e:
            self.logger.error(f"Error updating market metrics: {str(e)}")

    async def _calculate_sentiment(self) -> float:
        """Calculate overall market sentiment score"""
        try:
            weights = {
                'price_action': 0.25,
                'volume': 0.20,
                'social_sentiment': 0.15,
                'meta_momentum': 0.25,
                'liquidity_flow': 0.15
            }

            weighted_sum = sum(
                self._market_metrics[metric] * weight
                for metric, weight in weights.items()
            )

            return round(weighted_sum, 2)

        except Exception as e:
            self.logger.error(f"Error calculating sentiment: {str(e)}")
            return 50  # Neutral default

    def _classify_sentiment(self, sentiment: float) -> str:
        """Classify sentiment score"""
        if sentiment <= 25:
            return 'Extreme Fear'
        elif sentiment <= 45:
            return 'Fear'
        elif sentiment <= 55:
            return 'Neutral'
        elif sentiment <= 75:
            return 'Greed'
        else:
            return 'Extreme Greed'

    async def _get_volume_metrics(self) -> Dict:
        """Get detailed volume metrics"""
        try:
            # Implement volume metrics calculation
            return {
                'total_volume_24h': 0,
                'volume_change': 0,
                'average_volume_7d': 0
            }
        except Exception as e:
            self.logger.error(f"Error getting volume metrics: {str(e)}")
            return {}

    async def _get_liquidity_metrics(self) -> Dict:
        """Get detailed liquidity metrics"""
        try:
            # Implement liquidity metrics calculation
            return {
                'total_liquidity': 0,
                'liquidity_change_24h': 0,
                'liquidity_distribution': {}
            }
        except Exception as e:
            self.logger.error(f"Error getting liquidity metrics: {str(e)}")
            return {}

    async def _get_social_metrics(self) -> Dict:
        """Get social media metrics"""
        try:
            # Implement social metrics calculation
            return {
                'total_mentions': 0,
                'sentiment_score': 0,
                'engagement_rate': 0
            }
        except Exception as e:
            self.logger.error(f"Error getting social metrics: {str(e)}")
            return {}

    async def _check_sentiment_change(self) -> Dict:
        """Check for significant sentiment changes"""
        try:
            if len(self._sentiment_history) < 2:
                return {'is_significant': False}

            current = self._sentiment_history[-1]['value']
            previous = self._sentiment_history[-2]['value']
            change = current - previous

            return {
                'is_significant': abs(change) > 10,
                'severity': 'high' if abs(change) > 20 else 'medium',
                'message': f"Sentiment shifted by {change:+.1f} points"
            }

        except Exception as e:
            self.logger.error(f"Error checking sentiment change: {str(e)}")
            return {'is_significant': False}

    async def _check_volume_anomalies(self) -> List[Dict]:
        """Check for volume anomalies"""
        try:
            alerts = []
            volume_data = await self._get_volume_metrics()
            
            # Check for volume spikes
            if volume_data.get('volume_change', 0) > 100:
                alerts.append({
                    'type': 'volume_spike',
                    'severity': 'high',
                    'message': f"Trading volume increased by {volume_data['volume_change']}%"
                })

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking volume anomalies: {str(e)}")
            return []

    async def _check_liquidity_changes(self) -> List[Dict]:
        """Check for significant liquidity changes"""
        try:
            alerts = []
            liquidity_data = await self._get_liquidity_metrics()
            
            # Check for liquidity drops
            if liquidity_data.get('liquidity_change_24h', 0) < -20:
                alerts.append({
                    'type': 'liquidity_drop',
                    'severity': 'high',
                    'message': f"Market liquidity decreased by {abs(liquidity_data['liquidity_change_24h'])}%"
                })

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking liquidity changes: {str(e)}")
            return []

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key in self._cache:
            age = datetime.now() - self._cache[key]['timestamp']
            return age.seconds < self._cache_expiry
        return False

    def _update_sentiment_history(self, sentiment_data: Dict):
        """Update sentiment history"""
        try:
            self._sentiment_history.append(sentiment_data)
            
            # Keep only last 7 days of history
            cutoff = datetime.now() - timedelta(days=7)
            self._sentiment_history = [
                h for h in self._sentiment_history
                if datetime.fromisoformat(h['timestamp']) > cutoff
            ]

        except Exception as e:
            self.logger.error(f"Error updating sentiment history: {str(e)}")

    # Placeholder methods for metric calculations
    async def _calculate_price_action(self) -> float:
        """Calculate price action score"""
        return 50.0

    async def _calculate_volume_score(self) -> float:
        """Calculate volume score"""
        return 50.0

    async def _calculate_social_score(self) -> float:
        """Calculate social sentiment score"""
        return 50.0

    async def _calculate_meta_momentum(self) -> float:
        """Calculate meta momentum score"""
        return 50.0

    async def _calculate_liquidity_flow(self) -> float:
        """Calculate liquidity flow score"""
        return 50.0