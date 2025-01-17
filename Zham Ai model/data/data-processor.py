# model/data/process_training_data.py

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import Dict, List

class DataProcessor:
    def __init__(self):
        self.training_path = Path('training')
        self.historical_path = Path('historical')
        self.processed_path = Path('processed')

    def process_raw_data(self, raw_data_path: str):
        """Process raw data and save to training format"""
        # Load raw data
        with open(raw_data_path, 'r') as f:
            raw_data = json.load(f)

        # Process and format data
        processed_data = {
            "training_sets": {
                "meta_trends": {}
            },
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "entries_count": 0
        }

        # Process each meta category
        for meta_category in ['ai', 'gaming', 'meme', 'defi']:
            meta_data = self._process_meta_category(raw_data, meta_category)
            processed_data["training_sets"]["meta_trends"][meta_category] = meta_data
            processed_data["entries_count"] += len(meta_data)

        # Save processed data
        output_path = self.training_path / 'training_config.json'
        with open(output_path, 'w') as f:
            json.dump(processed_data, f, indent=4)

    def _process_meta_category(self, raw_data: Dict, category: str) -> List[Dict]:
        """Process data for a specific meta category"""
        processed_entries = []

        # Extract relevant entries
        for entry in raw_data:
            if self._is_relevant_to_category(entry, category):
                processed_entry = {
                    "text": entry["text"],
                    "market_data": {
                        "volume_24h": entry["volume_24h"],
                        "price_change_24h": entry["price_change_24h"],
                        "market_cap": entry["market_cap"],
                        "holder_count": entry["holders"],
                        "social_score": self._calculate_social_score(entry),
                        "liquidity_usd": entry["liquidity"]
                    },
                    "trend": self._determine_trend(entry),
                    "score": self._calculate_score(entry)
                }
                processed_entries.append(processed_entry)

        return processed_entries

    def _is_relevant_to_category(self, entry: Dict, category: str) -> bool:
        """Check if entry is relevant to meta category"""
        text = entry["text"].lower()
        name = entry.get("name", "").lower()
        
        category_keywords = {
            "ai": ["ai", "artificial", "intelligence", "bot", "neural"],
            "gaming": ["game", "play", "gaming", "p2e", "metaverse"],
            "meme": ["meme", "doge", "pepe", "wojak"],
            "defi": ["defi", "swap", "yield", "farm"]
        }

        return any(kw in text or kw in name for kw in category_keywords[category])

    def _calculate_social_score(self, entry: Dict) -> float:
        """Calculate social engagement score"""
        mentions = entry.get("social_mentions", 0)
        sentiment = entry.get("sentiment_score", 0)
        engagement = entry.get("social_engagement", 0)
        
        # Normalize and combine metrics
        normalized_mentions = min(mentions / 1000, 1)
        normalized_engagement = min(engagement / 10000, 1)
        sentiment_score = (sentiment + 1) / 2  # Convert -1,1 to 0,1
        
        return (normalized_mentions * 0.3 + 
                normalized_engagement * 0.3 + 
                sentiment_score * 0.4) * 100

    def _determine_trend(self, entry: Dict) -> int:
        """Determine trend category (0: bearish, 1: neutral, 2: bullish)"""
        price_change = entry.get("price_change_24h", 0)
        volume_change = entry.get("volume_change_24h", 0)
        
        if price_change > 10 and volume_change > 0:
            return 2  # bullish
        elif price_change < -10 or volume_change < -20:
            return 0  # bearish
        return 1  # neutral

    def _calculate_score(self, entry: Dict) -> float:
        """Calculate overall meta score"""
        factors = {
            "price_change": min(max(entry.get("price_change_24h", 0), -100), 100) / 100,
            "volume": min(entry.get("volume_24h", 0) / 1000000, 1),
            "holders": min(entry.get("holders", 0) / 1000, 1),
            "liquidity": min(entry.get("liquidity", 0) / 100000, 1)
        }
        
        weights = {
            "price_change": 0.3,
            "volume": 0.3,
            "holders": 0.2,
            "liquidity": 0.2
        }
        
        score = sum(factor * weights[name] for name, factor in factors.items())
        return min(max(score, 0), 1)

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_raw_data('raw/market_data.json')