# model/utils/metrics.py

import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import confusion_matrix, classification_report
import logging
from datetime import datetime

class MetricsCalculator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trend_labels = ['bearish', 'neutral', 'bullish']

    def calculate_trend_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate metrics for trend predictions"""
        try:
            # Calculate confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            # Calculate classification metrics
            report = classification_report(y_true, y_pred, 
                                        target_names=self.trend_labels,
                                        output_dict=True)
            
            # Calculate accuracy
            accuracy = np.mean(y_true == y_pred)
            
            return {
                'accuracy': accuracy,
                'confusion_matrix': cm.tolist(),
                'classification_report': report,
                'error_analysis': self._analyze_errors(y_true, y_pred),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error calculating trend metrics: {str(e)}")
            raise

    def calculate_score_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate metrics for score predictions"""
        try:
            # Calculate basic metrics
            mae = np.mean(np.abs(y_true - y_pred))
            mse = np.mean((y_true - y_pred) ** 2)
            rmse = np.sqrt(mse)
            
            # Calculate correlation
            correlation = np.corrcoef(y_true, y_pred)[0, 1]
            
            return {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'correlation': correlation,
                'error_distribution': self._analyze_score_errors(y_true, y_pred),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error calculating score metrics: {str(e)}")
            raise

    def calculate_performance_metrics(self, predictions: List[Dict], actuals: List[Dict]) -> Dict:
        """Calculate comprehensive performance metrics"""
        try:
            metrics = {
                'overall': {
                    'accuracy': 0,
                    'profit_factor': 0,
                    'win_rate': 0,
                },
                'by_meta': {},
                'time_analysis': self._analyze_time_performance(predictions, actuals),
                'risk_metrics': self._calculate_risk_metrics(predictions, actuals),
                'timestamp': datetime.now().isoformat()
            }

            # Calculate overall metrics
            total_predictions = len(predictions)
            correct_predictions = sum(1 for p, a in zip(predictions, actuals) if p['trend'] == a['trend'])
            
            metrics['overall']['accuracy'] = correct_predictions / total_predictions if total_predictions > 0 else 0
            
            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            raise

    def _analyze_errors(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Analyze prediction errors"""
        errors = []
        for true, pred in zip(y_true, y_pred):
            if true != pred:
                errors.append({
                    'true': self.trend_labels[true],
                    'predicted': self.trend_labels[pred],
                    'severity': self._calculate_error_severity(true, pred)
                })

        return {
            'total_errors': len(errors),
            'error_types': self._categorize_errors(errors),
            'severity_distribution': self._get_severity_distribution(errors)
        }

    def _calculate_error_severity(self, true: int, pred: int) -> str:
        """Calculate error severity based on prediction distance"""
        distance = abs(true - pred)
        if distance == 2:  # Opposite prediction (bearish vs bullish)
            return 'high'
        return 'medium' if distance == 1 else 'low'

    def _categorize_errors(self, errors: List[Dict]) -> Dict:
        """Categorize types of errors"""
        categories = {}
        for error in errors:
            key = f"{error['true']}_as_{error['predicted']}"
            categories[key] = categories.get(key, 0) + 1
        return categories

    def _get_severity_distribution(self, errors: List[Dict]) -> Dict:
        """Get distribution of error severities"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for error in errors:
            distribution[error['severity']] += 1
        return distribution

    def _analyze_score_errors(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Analyze score prediction errors"""
        errors = y_true - y_pred
        
        return {
            'mean_error': np.mean(errors),
            'std_error': np.std(errors),
            'percentiles': {
                '25': np.percentile(errors, 25),
                '50': np.percentile(errors, 50),
                '75': np.percentile(errors, 75)
            },
            'error_ranges': self._get_error_ranges(errors)
        }

    def _get_error_ranges(self, errors: np.ndarray) -> Dict:
        """Calculate distribution of errors in ranges"""
        ranges = {
            'very_low': (-0.1, 0.1),
            'low': (-0.2, 0.2),
            'medium': (-0.3, 0.3),
            'high': (-0.4, 0.4),
            'very_high': (-float('inf'), float('inf'))
        }
        
        distribution = {}
        for name, (min_val, max_val) in ranges.items():
            mask = (errors >= min_val) & (errors <= max_val)
            distribution[name] = np.sum(mask) / len(errors) * 100
        
        return distribution

    def _analyze_time_performance(self, predictions: List[Dict], actuals: List[Dict]) -> Dict:
        """Analyze performance over time"""
        try:
            time_periods = self._group_by_time_period(predictions, actuals)
            
            performance_by_period = {}
            for period, data in time_periods.items():
                period_predictions = data['predictions']
                period_actuals = data['actuals']
                
                # Calculate period metrics
                total = len(period_predictions)
                correct = sum(1 for p, a in zip(period_predictions, period_actuals) 
                            if p['trend'] == a['trend'])
                
                performance_by_period[period] = {
                    'accuracy': correct / total if total > 0 else 0,
                    'total_predictions': total,
                    'correct_predictions': correct
                }
            
            return performance_by_period

        except Exception as e:
            self.logger.error(f"Error analyzing time performance: {str(e)}")
            return {}

    def _calculate_risk_metrics(self, predictions: List[Dict], actuals: List[Dict]) -> Dict:
        """Calculate risk-adjusted performance metrics"""
        try:
            # Calculate returns
            returns = []
            for pred, actual in zip(predictions, actuals):
                if pred['trend'] == actual['trend']:
                    returns.append(actual.get('price_change', 0))
                else:
                    returns.append(-actual.get('price_change', 0))

            returns = np.array(returns)
            
            # Calculate metrics
            sharpe_ratio = np.mean(returns) / np.std(returns) if len(returns) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns)
            
            return {
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_ratio': np.mean(returns > 0) if len(returns) > 0 else 0,
                'profit_factor': self._calculate_profit_factor(returns),
                'risk_metrics': {
                    'var_95': np.percentile(returns, 5) if len(returns) > 0 else 0,
                    'var_99': np.percentile(returns, 1) if len(returns) > 0 else 0,
                    'expected_shortfall': np.mean(returns[returns < 0]) if len(returns) > 0 else 0
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {str(e)}")
            return {}

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = running_max - cumulative
        return np.max(drawdown) if len(drawdown) > 0 else 0

    def _calculate_profit_factor(self, returns: np.ndarray) -> float:
        """Calculate profit factor"""
        gains = returns[returns > 0]
        losses = abs(returns[returns < 0])
        
        total_gains = np.sum(gains)
        total_losses = np.sum(losses)
        
        return total_gains / total_losses if total_losses > 0 else 0

    def _group_by_time_period(self, predictions: List[Dict], actuals: List[Dict]) -> Dict:
        """Group predictions and actuals by time period"""
        periods = {}
        
        for pred, actual in zip(predictions, actuals):
            timestamp = datetime.fromisoformat(pred['timestamp'])
            period = timestamp.strftime('%Y-%m-%d')
            
            if period not in periods:
                periods[period] = {
                    'predictions': [],
                    'actuals': []
                }
            
            periods[period]['predictions'].append(pred)
            periods[period]['actuals'].append(actual)
        
        return periods