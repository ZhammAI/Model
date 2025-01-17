# model/utils/data_loader.py

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

class DataLoader:
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
    def load_training_data(self) -> Tuple[List, List]:
        """Load and parse training data"""
        try:
            config_path = self.data_dir / "training" / "training_config.json"
            with open(config_path, "r") as f:
                training_data = json.load(f)

            X = []  # Features
            y = []  # Labels
            
            for meta_category, entries in training_data["training_sets"]["meta_trends"].items():
                for entry in entries:
                    features = self._extract_features(entry)
                    labels = self._extract_labels(entry)
                    
                    X.append(features)
                    y.append(labels)

            return np.array(X), np.array(y)

        except Exception as e:
            self.logger.error(f"Error loading training data: {str(e)}")
            raise

    def load_historical_data(self, days: Optional[int] = None) -> Dict:
        """Load historical data"""
        try:
            history_path = self.data_dir / "historical" / "meta_history.json"
            with open(history_path, "r") as f:
                historical_data = json.load(f)

            if days:
                return self._filter_recent_data(historical_data, days)
            return historical_data

        except Exception as e:
            self.logger.error(f"Error loading historical data: {str(e)}")
            raise

    def _extract_features(self, entry: Dict) -> List:
        """Extract features from training entry"""
        market_data = entry["market_data"]
        return [
            market_data.get("volume_24h", 0),
            market_data.get("price_change_24h", 0),
            market_data.get("market_cap", 0),
            market_data.get("holder_count", 0),
            market_data.get("social_score", 0),
            market_data.get("liquidity_usd", 0)
        ]

    def _extract_labels(self, entry: Dict) -> List:
        """Extract labels from training entry"""
        return [
            entry["trend"],  # Classification label
            entry["score"]   # Regression score
        ]

    def _filter_recent_data(self, data: Dict, days: int) -> Dict:
        """Filter historical data for recent days"""
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        filtered_data = {
            "meta_trends": {},
            "market_conditions": [],
            "version": data["version"],
            "last_updated": data["last_updated"]
        }

        # Filter meta trends
        for meta, meta_data in data["meta_trends"].items():
            filtered_data["meta_trends"][meta] = {
                "daily_data": [
                    d for d in meta_data["daily_data"]
                    if d["date"] >= cutoff_date
                ],
                "performance_metrics": meta_data["performance_metrics"]
            }

        # Filter market conditions
        filtered_data["market_conditions"] = [
            c for c in data["market_conditions"]
            if c["date"] >= cutoff_date
        ]

        return filtered_data

    def batch_generator(self, X: np.ndarray, y: np.ndarray, batch_size: int):
        """Generate batches for training"""
        indices = np.arange(len(X))
        while True:
            np.random.shuffle(indices)
            for i in range(0, len(X), batch_size):
                batch_indices = indices[i:i + batch_size]
                yield X[batch_indices], y[batch_indices]