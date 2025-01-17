# model/data/update_historical.py (continued)

                'dates': [d['date'] for d in recent_data],
                'days_analyzed': days
            }

        except Exception as e:
            self.logger.error(f"Error getting meta performance: {str(e)}")
            return {}

    def get_market_overview(self, days: int = 7) -> Dict:
        """Get overall market overview for specified period"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)

            cutoff_date = (
                datetime.now() - timedelta(days=days)
            ).strftime('%Y-%m-%d')

            recent_conditions = [
                c for c in data['market_conditions']
                if c['date'] >= cutoff_date
            ]

            if not recent_conditions:
                return {}

            # Aggregate data
            overview = {
                'sentiment_trend': self._calculate_sentiment_trend(recent_conditions),
                'volume_trend': self._calculate_volume_trend(recent_conditions),
                'active_metas': self._get_active_metas(recent_conditions),
                'market_score_avg': sum(
                    c.get('market_score', 0) for c in recent_conditions
                ) / len(recent_conditions),
                'dates': [c['date'] for c in recent_conditions]
            }

            return overview

        except Exception as e:
            self.logger.error(f"Error getting market overview: {str(e)}")
            return {}

    def _calculate_sentiment_trend(self, conditions: List[Dict]) -> str:
        """Calculate overall sentiment trend"""
        if not conditions:
            return 'neutral'

        sentiment_values = {
            'bullish': 1,
            'neutral': 0,
            'bearish': -1
        }

        recent_sentiments = [
            sentiment_values.get(c.get('overall_sentiment', 'neutral'), 0)
            for c in conditions
        ]

        avg_sentiment = sum(recent_sentiments) / len(recent_sentiments)

        if avg_sentiment > 0.3:
            return 'improving'
        elif avg_sentiment < -0.3:
            return 'declining'
        return 'stable'

    def _calculate_volume_trend(self, conditions: List[Dict]) -> Dict:
        """Calculate volume trend metrics"""
        if len(conditions) < 2:
            return {'trend': 'neutral', 'change': 0}

        volumes = [c.get('total_volume', 0) for c in conditions]
        avg_start = sum(volumes[:3]) / 3 if len(volumes) >= 3 else volumes[0]
        avg_end = sum(volumes[-3:]) / 3 if len(volumes) >= 3 else volumes[-1]

        change_pct = ((avg_end - avg_start) / avg_start * 100) if avg_start > 0 else 0

        return {
            'trend': 'increasing' if change_pct > 10 else 'decreasing' if change_pct < -10 else 'stable',
            'change': round(change_pct, 2)
        }

    def _get_active_metas(self, conditions: List[Dict]) -> List[Dict]:
        """Get list of active metas with their frequency"""
        meta_counts = {}
        total_records = len(conditions)

        for condition in conditions:
            active_metas = condition.get('active_metas', [])
            for meta in active_metas:
                meta_counts[meta] = meta_counts.get(meta, 0) + 1

        # Calculate frequency and sort
        active_metas = [
            {
                'name': meta,
                'frequency': count / total_records * 100
            }
            for meta, count in meta_counts.items()
        ]

        return sorted(active_metas, key=lambda x: x['frequency'], reverse=True)

    def export_training_data(self, days: int = 30) -> List[Dict]:
        """Export historical data in training format"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)

            cutoff_date = (
                datetime.now() - timedelta(days=days)
            ).strftime('%Y-%m-%d')

            training_data = []
            for meta_name, meta_data in data['meta_trends'].items():
                daily_data = [
                    d for d in meta_data.get('daily_data', [])
                    if d['date'] >= cutoff_date
                ]

                for day_data in daily_data:
                    for token in day_data.get('top_tokens', []):
                        training_data.append({
                            'text': self._generate_training_text(meta_name, day_data),
                            'market_data': {
                                'volume_24h': token.get('volume_24h', 0),
                                'price_change_24h': token.get('price_change', 0),
                                'market_cap': token.get('market_cap', 0),
                                'holder_count': token.get('holders', 0),
                                'liquidity_usd': token.get('liquidity', 0),
                                'social_score': day_data.get('sentiment_score', 50)
                            },
                            'trend': self._determine_trend(token),
                            'score': day_data.get('trend_score', 50) / 100
                        })

            return training_data

        except Exception as e:
            self.logger.error(f"Error exporting training data: {str(e)}")
            return []

    def _generate_training_text(self, meta_name: str, data: Dict) -> str:
        """Generate descriptive text for training data"""
        sentiment = data.get('sentiment_score', 0)
        sentiment_text = 'positive' if sentiment > 0.3 else 'negative' if sentiment < -0.3 else 'neutral'
        
        return f"{meta_name} trend showing {sentiment_text} sentiment with {data.get('mentions', 0)} mentions. Market activity indicates {data.get('volume_total', 0)} daily volume."


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = HistoricalDataManager()
    
    # Example usage
    new_data = {
        'meta_trends': {
            'ai': {
                'mentions': 1500,
                'sentiment_score': 0.75,
                'volume_total': 5000000,
                'trend_score': 85
            }
        },
        'market_conditions': {
            'overall_sentiment': 'bullish',
            'total_volume': 50000000,
            'active_metas': ['ai', 'gaming'],
            'market_score': 75
        }
    }
    
    manager.update_historical_data(new_data)