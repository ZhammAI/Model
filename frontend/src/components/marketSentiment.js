// src/services/marketSentiment.js

import { 
    SENTIMENT_THRESHOLDS, 
    TIME_CONSTANTS,
    MARKET_STATUS 
  } from '../utils/constants';
  import { calculatePercentageChange, calculateEMA } from '../utils/helpers';
  
  class MarketSentiment {
    constructor() {
      this.metrics = {
        priceAction: 0,
        volume: 0,
        socialSentiment: 0,
        metaMomentum: 0,
        liquidityFlow: 0
      };
      this.historicalSentiment = [];
      this.lastUpdate = 0;
    }
  
    /**
     * Calculate overall market sentiment
     * @param {Object} marketData - Current market data
     * @param {Array} metaTrends - Current meta trends
     * @returns {Object} Sentiment analysis
     */
    calculateSentiment(marketData, metaTrends) {
      this.updateMetrics(marketData, metaTrends);
      const sentiment = this.calculateOverallSentiment();
      this.updateHistoricalData(sentiment);
  
      return {
        value: sentiment,
        classification: this.classifySentiment(sentiment),
        metrics: this.metrics,
        trend: this.analyzeSentimentTrend(),
        marketStatus: this.determineMarketStatus()
      };
    }
  
    /**
     * Update individual sentiment metrics
     * @param {Object} marketData - Market data
     * @param {Array} metaTrends - Meta trends
     */
    updateMetrics(marketData, metaTrends) {
      // Price Action Analysis (0-100)
      this.metrics.priceAction = this.analyzePriceAction(marketData.priceData);
  
      // Volume Analysis (0-100)
      this.metrics.volume = this.analyzeVolume(marketData.volumeData);
  
      // Social Sentiment (0-100)
      this.metrics.socialSentiment = this.analyzeSocialSentiment(marketData.socialData);
  
      // Meta Momentum (-100 to 100, normalized to 0-100)
      this.metrics.metaMomentum = this.analyzeMetaMomentum(metaTrends);
  
      // Liquidity Flow (0-100)
      this.metrics.liquidityFlow = this.analyzeLiquidityFlow(marketData.liquidityData);
    }
  
    /**
     * Update historical sentiment data
     * @param {number} sentiment - Current sentiment value
     */
    updateHistoricalData(sentiment) {
      const currentTime = Date.now();
      this.historicalSentiment.push({
        timestamp: currentTime,
        value: sentiment
      });
  
      // Keep only last 7 days of data
      const weekAgo = currentTime - TIME_CONSTANTS.ONE_WEEK;
      this.historicalSentiment = this.historicalSentiment.filter(
        data => data.timestamp >= weekAgo
      );
  
      this.lastUpdate = currentTime;
    }
  
    /**
     * Calculate volatility from price history
     * @param {Array} priceHistory - Historical price data
     * @returns {number} Volatility score
     */
    calculateVolatility(priceHistory) {
      if (priceHistory.length < 2) return 0;
  
      const returns = [];
      for (let i = 1; i < priceHistory.length; i++) {
        const percentChange = calculatePercentageChange(
          priceHistory[i],
          priceHistory[i - 1]
        );
        returns.push(percentChange);
      }
  
      const mean = returns.reduce((sum, val) => sum + val, 0) / returns.length;
      const squaredDiffs = returns.map(val => Math.pow(val - mean, 2));
      const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / returns.length;
  
      return Math.sqrt(variance);
    }
  
    /**
     * Calculate volume trend
     * @param {Array} volumeHistory - Historical volume data
     * @returns {number} Volume trend score (-1 to 1)
     */
    calculateVolumeTrend(volumeHistory) {
      if (volumeHistory.length < 2) return 0;
  
      const shortTermEMA = calculateEMA(volumeHistory.slice(-7), 7);
      const longTermEMA = calculateEMA(volumeHistory, volumeHistory.length);
  
      return Math.tanh((shortTermEMA - longTermEMA) / longTermEMA);
    }
  
    /**
     * Calculate liquidity stability
     * @param {Array} liquidityHistory - Historical liquidity data
     * @returns {number} Stability score (0-100)
     */
    calculateLiquidityStability(liquidityHistory) {
      if (liquidityHistory.length < 2) return 50;
  
      const changes = [];
      for (let i = 1; i < liquidityHistory.length; i++) {
        const change = Math.abs(calculatePercentageChange(
          liquidityHistory[i],
          liquidityHistory[i - 1]
        ));
        changes.push(change);
      }
  
      const averageChange = changes.reduce((sum, val) => sum + val, 0) / changes.length;
      return Math.max(0, 100 - averageChange);
    }
  
    /**
     * Determine overall market status
     * @returns {string} Market status
     */
    determineMarketStatus() {
      const sentiment = this.calculateOverallSentiment();
      const trend = this.analyzeSentimentTrend();
      
      if (sentiment >= SENTIMENT_THRESHOLDS.GREED && trend.direction === 'positive') {
        return MARKET_STATUS.BULL;
      }
      
      if (sentiment <= SENTIMENT_THRESHOLDS.FEAR && trend.direction === 'negative') {
        return MARKET_STATUS.BEAR;
      }
      
      if (trend.strength === 'weak') {
        return MARKET_STATUS.CONSOLIDATION;
      }
      
      if (sentiment > SENTIMENT_THRESHOLDS.FEAR && trend.direction === 'positive') {
        return MARKET_STATUS.RECOVERY;
      }
  
      return MARKET_STATUS.CONSOLIDATION;
    }
  
    /**
     * Get recommendations based on current sentiment
     * @returns {Object} Trading recommendations
     */
    getRecommendations() {
      const sentiment = this.calculateOverallSentiment();
      const status = this.determineMarketStatus();
      const trend = this.analyzeSentimentTrend();
  
      return {
        sentiment,
        status,
        trend,
        suggestions: this.generateSuggestions(sentiment, status, trend),
        riskLevel: this.calculateRiskLevel(sentiment, status, trend)
      };
    }
  
    /**
     * Generate trading suggestions
     * @param {number} sentiment - Current sentiment
     * @param {string} status - Market status
     * @param {Object} trend - Trend analysis
     * @returns {Array} Trading suggestions
     */
    generateSuggestions(sentiment, status, trend) {
      const suggestions = [];
  
      if (status === MARKET_STATUS.BULL && trend.strength === 'strong') {
        suggestions.push('Consider taking profits on strong performers');
        suggestions.push('Watch for potential trend exhaustion');
      } else if (status === MARKET_STATUS.BEAR && trend.strength === 'strong') {
        suggestions.push('Consider reducing exposure');
        suggestions.push('Watch for reversal signals');
      } else if (status === MARKET_STATUS.RECOVERY) {
        suggestions.push('Look for strong projects with good fundamentals');
        suggestions.push('Consider gradual position building');
      } else {
        suggestions.push('Maintain balanced portfolio');
        suggestions.push('Focus on risk management');
      }
  
      return suggestions;
    }
  
    /**
     * Calculate current risk level
     * @param {number} sentiment - Current sentiment
     * @param {string} status - Market status
     * @param {Object} trend - Trend analysis
     * @returns {string} Risk level
     */
    calculateRiskLevel(sentiment, status, trend) {
      if (sentiment >= SENTIMENT_THRESHOLDS.EXTREME_GREED) return 'Very High';
      if (sentiment <= SENTIMENT_THRESHOLDS.EXTREME_FEAR) return 'High';
      if (trend.strength === 'strong') return 'Moderate';
      return 'Normal';
    }
  }
  
  export default MarketSentiment;