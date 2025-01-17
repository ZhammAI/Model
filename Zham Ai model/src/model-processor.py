# model/src/processor.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from textblob import TextBlob
from nltk.tokenize import word_tokenize
import re

class DataProcessor:
    def __init__(self):
        self.required_metrics = [
            'volume_24h',
            'price_change_24h',
            'market_cap',
            'holder_count',
            'social_score',
            'liquidity_usd',
            'tx_count_24h',
            'age_hours',
            'unique_holders_ratio',
            'volume_market_cap_ratio'
        ]

    def prepare_market_data(self, raw_data: Dict) -> np.ndarray:
        """Process market metrics into model input format"""
        metrics = []
        for metric in self.required_metrics:
            value = raw_data.get(metric, 0)
            # Apply necessary transformations
            if metric in ['volume_24h', 'market_cap', 'liquidity_usd']:
                value = np.log1p(value)  # Log transform large numbers
            elif metric in ['price_change_24h']:
                value = value / 100  # Normalize percentages
            metrics.append(value)
        
        return np.array(metrics)

    def process_social_data(self, texts: List[str]) -> Dict:
        """Process social media texts"""
        processed = []
        sentiments = []
        
        for text in texts:
            # Clean text
            clean_text = self._clean_text(text)
            
            # Get sentiment
            sentiment = TextBlob(clean_text).sentiment
            sentiments.append({
                'polarity': sentiment.polarity,
                'subjectivity': sentiment.subjectivity
            })
            
            # Extract features
            processed.append({
                'text': clean_text,
                'tokens': word_tokenize(clean_text),
                'sentiment': sentiment,
                'word_count': len(clean_text.split()),
                'has_links': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
                'has_cashtags': bool(re.search(r'\$\w+', text))
            })

        return {
            'processed_texts': processed,
            'sentiment_stats': {
                'avg_polarity': np.mean([s['polarity'] for s in sentiments]),
                'avg_subjectivity': np.mean([s['subjectivity'] for s in sentiments]),
                'sentiment_std': np.std([s['polarity'] for s in sentiments])
            }
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags symbol but keep text
        text = re.sub(r'#', '', text)
        
        # Remove cashtags but keep symbol
        text = re.sub(r'\$\w+', 'TOKEN', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def calculate_meta_score(self, market_data: Dict, social_data: Dict) -> float:
        """Calculate meta trend score"""
        # Market metrics weight: 60%
        market_score = self._calculate_market_score(market_data)
        
        # Social metrics weight: 40%
        social_score = self._calculate_social_score(social_data)
        
        return (market_score * 0.6) + (social_score * 0.4)

    def _calculate_market_score(self, data: Dict) -> float:
        """Calculate market metrics score"""
        scores = []
        
        # Volume score
        volume_mcap_ratio = data.get('volume_24h', 0) / max(data.get('market_cap', 1), 1)
        scores.append(min(volume_mcap_ratio * 100, 100))
        
        # Price action score
        price_change = data.get('price_change_24h', 0)
        scores.append(50 + (price_change / 2))  # Center at 50
        
        # Holder metrics
        holder_growth = data.get('holder_growth_24h', 0)
        scores.append(min(holder_growth * 10, 100))
        
        # Liquidity score
        liquidity_mcap_ratio = data.get('liquidity_usd', 0) / max(data.get('market_cap', 1), 1)
        scores.append(min(liquidity_mcap_ratio * 200, 100))
        
        return np.mean(scores)

    def _calculate_social_score(self, data: Dict) -> float:
        """Calculate social metrics score"""
        sentiment_stats = data.get('sentiment_stats', {})
        
        # Base score from sentiment
        base_score = 50 + (sentiment_stats.get('avg_polarity', 0) * 50)
        
        # Adjust for subjectivity
        subjectivity = sentiment_stats.get('avg_subjectivity', 0.5)
        confidence_factor = 1 - (abs(subjectivity - 0.5) * 0.5)
        
        # Adjust for sentiment consistency
        consistency_factor = 1 - min(sentiment_stats.get('sentiment_std', 0), 0.5)
        
        return base_score * confidence_factor * consistency_factor

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize feature array"""
        return (features - np.mean(features, axis=0)) / np.std(features, axis=0)