# backend/src/services/twitter_service.py

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import tweepy
from collections import defaultdict
from textblob import TextBlob

class TwitterService:
    def __init__(self):
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        self.logger = logging.getLogger(__name__)
        self.cached_data = {}
        self.cache_expiry = 300  # 5 minutes cache

    async def track_memecoin_mentions(self, symbols: List[str]) -> Dict:
        """
        Track mentions and sentiment for specified memecoin symbols
        """
        try:
            current_time = datetime.utcnow()
            results = defaultdict(lambda: {
                'mentions': 0,
                'sentiment_score': 0,
                'positive_mentions': 0,
                'negative_mentions': 0,
                'related_metas': set(),
                'recent_tweets': []
            })

            # Create search query for all symbols
            query = ' OR '.join([f'#{symbol} OR ${symbol}' for symbol in symbols])
            query += ' -is:retweet lang:en'

            # Get tweets from the last hour
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics']
            )

            if not tweets.data:
                return dict(results)

            for tweet in tweets.data:
                # Analyze each tweet
                text = tweet.text.lower()
                sentiment = TextBlob(text).sentiment.polarity

                # Find mentioned symbols in tweet
                for symbol in symbols:
                    if f'#{symbol.lower()}' in text or f'${symbol.lower()}' in text:
                        data = results[symbol]
                        data['mentions'] += 1
                        data['sentiment_score'] += sentiment
                        
                        if sentiment > 0:
                            data['positive_mentions'] += 1
                        elif sentiment < 0:
                            data['negative_mentions'] += 1

                        # Extract related metas from tweet
                        data['related_metas'].update(self._extract_metas(text))
                        
                        # Store recent tweet data
                        data['recent_tweets'].append({
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'metrics': tweet.public_metrics
                        })

            # Calculate average sentiment and format results
            formatted_results = {}
            for symbol, data in results.items():
                if data['mentions'] > 0:
                    formatted_results[symbol] = {
                        'mentions': data['mentions'],
                        'average_sentiment': data['sentiment_score'] / data['mentions'],
                        'positive_mentions': data['positive_mentions'],
                        'negative_mentions': data['negative_mentions'],
                        'related_metas': list(data['related_metas']),
                        'recent_tweets': data['recent_tweets'][:5]  # Keep only 5 most recent
                    }

            return formatted_results

        except Exception as e:
            self.logger.error(f"Error tracking memecoin mentions: {str(e)}")
            return {}

    async def analyze_meta_trends(self) -> Dict:
        """
        Analyze meta trends from Twitter discussions
        """
        try:
            meta_keywords = [
                'ai', 'defi', 'gaming', 'meme', 'nft', 'metaverse',
                'web3', 'dao', 'play2earn', 'gamefi'
            ]
            
            results = defaultdict(lambda: {
                'mentions': 0,
                'engagement': 0,
                'sentiment': 0,
                'tweet_count': 0
            })

            # Search for meta-related tweets
            query = ' OR '.join([f'#{kw}' for kw in meta_keywords])
            query += ' solana OR #solana -is:retweet lang:en'

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics']
            )

            if not tweets.data:
                return {}

            for tweet in tweets.data:
                text = tweet.text.lower()
                metrics = tweet.public_metrics
                engagement = (
                    metrics.get('like_count', 0) +
                    metrics.get('retweet_count', 0) * 2 +
                    metrics.get('reply_count', 0) * 3
                )

                for keyword in meta_keywords:
                    if f'#{keyword}' in text:
                        results[keyword]['mentions'] += 1
                        results[keyword]['engagement'] += engagement
                        results[keyword]['sentiment'] += TextBlob(text).sentiment.polarity
                        results[keyword]['tweet_count'] += 1

            # Calculate scores and format results
            formatted_results = {}
            total_mentions = sum(data['mentions'] for data in results.values())

            for keyword, data in results.items():
                if data['tweet_count'] > 0:
                    formatted_results[keyword] = {
                        'mentions': data['mentions'],
                        'percentage': (data['mentions'] / total_mentions * 100) if total_mentions else 0,
                        'engagement_score': data['engagement'] / data['tweet_count'],
                        'average_sentiment': data['sentiment'] / data['tweet_count']
                    }

            return formatted_results

        except Exception as e:
            self.logger.error(f"Error analyzing meta trends: {str(e)}")
            return {}

    def _extract_metas(self, text: str) -> set:
        """
        Extract meta keywords from tweet text
        """
        common_metas = {
            'ai', 'defi', 'gaming', 'meme', 'nft', 'metaverse',
            'web3', 'dao', 'play2earn', 'gamefi'
        }
        found_metas = set()
        
        words = text.lower().split()
        hashtags = {word[1:] for word in words if word.startswith('#')}
        
        return hashtags.intersection(common_metas)

    async def get_influencer_activity(self, influencer_usernames: List[str]) -> Dict:
        """
        Track crypto influencer activity related to memecoins
        """
        try:
            results = {}
            
            for username in influencer_usernames:
                user = self.client.get_user(username=username)
                if not user.data:
                    continue

                user_id = user.data.id
                tweets = self.client.get_users_tweets(
                    id=user_id,
                    max_results=10,
                    tweet_fields=['created_at', 'public_metrics']
                )

                if not tweets.data:
                    continue

                relevant_tweets = []
                for tweet in tweets.data:
                    if any(keyword in tweet.text.lower() for keyword in ['solana', 'sol', 'memecoin']):
                        relevant_tweets.append({
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'metrics': tweet.public_metrics,
                            'sentiment': TextBlob(tweet.text).sentiment.polarity
                        })

                if relevant_tweets:
                    results[username] = relevant_tweets

            return results

        except Exception as e:
            self.logger.error(f"Error getting influencer activity: {str(e)}")
            return {}

# Example usage:
"""
twitter_service = TwitterService()

# Track specific memecoins
memecoin_data = await twitter_service.track_memecoin_mentions(['BONK', 'MYRO', 'WIF'])

# Analyze meta trends
meta_trends = await twitter_service.analyze_meta_trends()

# Track influencer activity
influencer_data = await twitter_service.get_influencer_activity([
    'DegenSpartan',
    'solana',
    'rothschilds'
])
"""