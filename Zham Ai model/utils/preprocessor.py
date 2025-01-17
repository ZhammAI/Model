# model/utils/preprocessor.py

import numpy as np
from typing import Dict, List, Union
from sklearn.preprocessing import StandardScaler
import re
from textblob import TextBlob
import logging

class Preprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        self.feature_names = [
            'volume_24h',
            'price_change_24h',
            'market_cap',
            'holder_count',
            'social_score',
            'liquidity_usd'
        ]

    def preprocess_market_data(self, data: Union[Dict, List[Dict]], fit: bool = False) -> np.ndarray:
        """Preprocess market data features"""
        try:
            if isinstance(data, dict):
                features = self._extract_market_features([data])
            else:
                features = self._extract_market_features(data)

            if fit:
                return self.scaler.fit_transform(features)
            return self.scaler.transform(features)

        except Exception as e:
            self.logger.error(f"Error preprocessing market data: {str(e)}")
            raise

    def preprocess_text(self, text: str) -> Dict:
        """Preprocess text data"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Get sentiment
            sentiment = TextBlob(cleaned_text).sentiment
            
            # Extract features
            features = {
                'cleaned_text': cleaned_text,
                'sentiment_polarity': sentiment.polarity,
                'sentiment_subjectivity': sentiment.subjectivity,
                'word_count': len(cleaned_text.split()),
                'contains_links': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
                'contains_numbers': bool(re.search(r'\d+', text)),
                'contains_cashtags': bool(re.search(r'\$\w+', text))
            }

            return features

        except Exception as e:
            self.logger.error(f"Error preprocessing text: {str(e)}")
            raise

    def _extract_market_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from market data"""
        features = []
        for entry in data:
            feature_vector = []
            for feature in self.feature_names:
                value = entry.get(feature, 0)
                
                # Apply transformations
                if feature in ['volume_24h', 'market_cap', 'liquidity_usd']:
                    value = np.log1p(value)
                elif feature in ['price_change_24h']:
                    value = value / 100
                
                feature_vector.append(value)
            features.append(feature_vector)
        
        return np.array(features)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def normalize_score(self, score: float) -> float:
        """Normalize score to 0-1 range"""
        return max(0, min(1, score))

    def process_batch(self, batch_data: List[Dict]) -> Dict:
        """Process a batch of data"""
        try:
            market_features = []
            text_features = []
            scores = []

            for entry in batch_data:
                # Process market data
                market_features.append(
                    self._extract_market_features([entry['market_data']])[0]
                )
                
                # Process text
                text_features.append(
                    self.preprocess_text(entry['text'])
                )
                
                # Process score
                scores.append(self.normalize_score(entry.get('score', 0)))

            return {
                'market_features': np.array(market_features),
                'text_features': text_features,
                'scores': np.array(scores)
            }

        except Exception as e:
            self.logger.error(f"Error processing batch: {str(e)}")
            raise

    def get_feature_importance(self, model, feature_names: List[str] = None) -> Dict:
        """Calculate feature importance"""
        if not feature_names:
            feature_names = self.feature_names

        try:
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]

            return {
                'features': [feature_names[i] for i in indices],
                'importance': [importances[i] for i in indices]
            }

        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {str(e)}")
            return {}