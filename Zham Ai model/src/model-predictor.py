# model/src/predictor.py

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging
from .model import ZhamModel
from .processor import DataProcessor

class Predictor:
    def __init__(self, model_path: Optional[str] = None):
        self.model = ZhamModel()
        self.processor = DataProcessor()
        self.logger = logging.getLogger(__name__)
        
        if model_path:
            self.load_model(model_path)
            
        self.trend_labels = ['bearish', 'neutral', 'bullish']

    def load_model(self, path: str):
        """Load trained model weights"""
        try:
            self.model.load_weights(path)
            self.logger.info(f"Model loaded from {path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise

    def predict(self, data: Dict) -> Dict:
        """Make predictions for new data"""
        try:
            # Process input data
            processed_text = self.processor._clean_text(data['text'])
            processed_metrics = self.processor.prepare_market_data(data['market_data'])

            # Get model prediction
            predictions = self.model.predict(processed_text, processed_metrics)

            # Add confidence metrics
            result = {
                **predictions,
                'meta_score': self.processor.calculate_meta_score(
                    data['market_data'],
                    data.get('social_data', {})
                ),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Add risk assessment
            result['risk_assessment'] = self._assess_risk(
                predictions,
                data['market_data']
            )

            return result

        except Exception as e:
            self.logger.error(f"Prediction error: {str(e)}")
            raise

    def predict_batch(self, data_list: List[Dict]) -> List[Dict]:
        """Make predictions for multiple items"""
        try:
            predictions = []
            for data in data_list:
                pred = self.predict(data)
                predictions.append(pred)
            return predictions
        except Exception as e:
            self.logger.error(f"Batch prediction error: {str(e)}")
            raise

    def _assess_risk(self, predictions: Dict, market_data: Dict) -> Dict:
        """Assess risk level based on predictions and market data"""
        try:
            # Base risk on prediction confidence
            confidence = predictions['trend_confidence']
            
            # Consider market metrics
            volume_mcap_ratio = (
                market_data.get('volume_24h', 0) / 
                max(market_data.get('market_cap', 1), 1)
            )
            
            holder_count = market_data.get('holder_count', 0)
            liquidity = market_data.get('liquidity_usd', 0)
            
            # Calculate risk factors
            risk_factors = {
                'confidence_risk': 1 - confidence,
                'volume_risk': max(0, 1 - volume_mcap_ratio),
                'holder_risk': max(0, 1 - (holder_count / 1000)),
                'liquidity_risk': max(0, 1 - (liquidity / 100000))
            }
            
            # Calculate overall risk score
            risk_score = np.mean(list(risk_factors.values())) * 100
            
            # Determine risk level
            if risk_score < 20:
                risk_level = 'low'
            elif risk_score < 50:
                risk_level = 'moderate'
            elif risk_score < 80:
                risk_level = 'high'
            else:
                risk_level = 'very_high'

            return {
                'score': risk_score,
                'level': risk_level,
                'factors': risk_factors
            }

        except Exception as e:
            self.logger.error(f"Risk assessment error: {str(e)}")
            return {
                'score': 100,
                'level': 'unknown',
                'factors': {}
            }

    def analyze_confidence(self, predictions: Dict) -> Dict:
        """Analyze prediction confidence levels"""
        try:
            trend_probs = predictions['probabilities']
            
            # Calculate entropy as uncertainty measure
            entropy = -sum(
                p * np.log2(p) if p > 0 else 0
                for p in trend_probs.values()
            )
            
            # Max entropy for 3 classes is log2(3)
            max_entropy = np.log2(3)
            certainty = 1 - (entropy / max_entropy)
            
            return {
                'certainty_score': certainty * 100,
                'entropy': entropy,
                'is_confident': certainty > 0.8,
                'confidence_level': 'high' if certainty > 0.8 else 'moderate' if certainty > 0.5 else 'low'
            }

        except Exception as e:
            self.logger.error(f"Confidence analysis error: {str(e)}")
            return {
                'certainty_score': 0,
                'entropy': max_entropy,
                'is_confident': False,
                'confidence_level': 'unknown'
            }

    def validate_prediction(self, prediction: Dict, threshold: float = 0.8) -> bool:
        """Validate prediction confidence"""
        return (
            prediction['trend_confidence'] >= threshold and
            prediction.get('meta_score', 0) >= 50 and
            prediction.get('risk_assessment', {}).get('level') not in ['high', 'very_high']
        )