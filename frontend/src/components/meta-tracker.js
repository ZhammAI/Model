// src/services/metaTracker.js

import { COMMON_METAS, TIME_CONSTANTS } from '../utils/constants';
import { findMatchingKeywords, calculatePercentageChange } from '../utils/helpers';

class MetaTracker {
  constructor() {
    this.metaTrends = new Map();
    this.historicalData = new Map();
    this.updateInterval = TIME_CONSTANTS.FIVE_MINUTES;
    this.lastUpdate = 0;
  }

  /**
   * Update meta trends with new token data
   * @param {Array} tokens - Array of token data
   * @returns {Object} Current meta trends
   */
  updateTrends(tokens) {
    const currentTime = Date.now();
    const trendData = new Map();
    let totalVolume = 0;

    // Process each token
    tokens.forEach(token => {
      // Calculate token's weight based on volume and price change
      const weight = this.calculateTokenWeight(token);
      totalVolume += token.volume24h || 0;

      // Extract and process metas from token
      const metas = this.extractMetas(token);
      metas.forEach(meta => {
        const currentWeight = trendData.get(meta) || 0;
        trendData.set(meta, currentWeight + weight);
      });
    });

    // Calculate percentages and store historical data
    this.updateHistoricalData(trendData, totalVolume, currentTime);
    this.lastUpdate = currentTime;

    return this.formatTrendData();
  }

  /**
   * Extract metas from token data
   * @param {Object} token - Token data
   * @returns {Array} Array of matched metas
   */
  extractMetas(token) {
    const textToAnalyze = `${token.name} ${token.symbol} ${token.description || ''}`.toLowerCase();
    return findMatchingKeywords(textToAnalyze, COMMON_METAS);
  }

  /**
   * Calculate token's weight for trend analysis
   * @param {Object} token - Token data
   * @returns {number} Token weight
   */
  calculateTokenWeight(token) {
    const volumeWeight = token.volume24h || 0;
    const priceChangeWeight = Math.max(0, token.priceChange24h || 0);
    const holdersWeight = Math.min(token.holders || 0, 10000) / 100;

    return volumeWeight * (1 + priceChangeWeight/100) * (1 + holdersWeight/100);
  }

  /**
   * Update historical trend data
   * @param {Map} trendData - Current trend data
   * @param {number} totalVolume - Total volume
   * @param {number} timestamp - Current timestamp
   */
  updateHistoricalData(trendData, totalVolume, timestamp) {
    // Convert to percentages
    const percentages = new Map();
    trendData.forEach((weight, meta) => {
      const percentage = (weight / totalVolume) * 100;
      percentages.set(meta, percentage);
    });

    // Store historical data
    this.historicalData.set(timestamp, percentages);

    // Keep only last 24 hours of data
    const dayAgo = timestamp - TIME_CONSTANTS.ONE_DAY;
    for (const [time] of this.historicalData) {
      if (time < dayAgo) {
        this.historicalData.delete(time);
      }
    }

    this.metaTrends = percentages;
  }

  /**
   * Format trend data for display
   * @returns {Object} Formatted trend data
   */
  formatTrendData() {
    const trends = Array.from(this.metaTrends.entries())
      .map(([meta, percentage]) => ({
        meta,
        percentage,
        change24h: this.calculate24hChange(meta)
      }))
      .sort((a, b) => b.percentage - a.percentage);

    return {
      trending: trends.slice(0, 5),
      rising: trends
        .filter(t => t.change24h > 5)
        .slice(0, 4),
      declining: trends
        .filter(t => t.change24h < -5)
        .slice(0, 4)
    };
  }

  /**
   * Calculate 24-hour change for a meta
   * @param {string} meta - Meta name
   * @returns {number} Percentage change
   */
  calculate24hChange(meta) {
    const times = Array.from(this.historicalData.keys()).sort();
    if (times.length < 2) return 0;

    const current = this.metaTrends.get(meta) || 0;
    const oldestData = this.historicalData.get(times[0]);
    const previous = oldestData.get(meta) || 0;

    return calculatePercentageChange(current, previous);
  }

  /**
   * Get meta momentum score
   * @param {string} meta - Meta name
   * @returns {number} Momentum score (-100 to 100)
   */
  getMetaMomentum(meta) {
    const changes = [];
    const timestamps = Array.from(this.historicalData.keys()).sort();
    
    for (let i = 1; i < timestamps.length; i++) {
      const currentData = this.historicalData.get(timestamps[i]);
      const previousData = this.historicalData.get(timestamps[i-1]);
      
      const current = currentData.get(meta) || 0;
      const previous = previousData.get(meta) || 0;
      
      changes.push(calculatePercentageChange(current, previous));
    }
    
    if (changes.length === 0) return 0;
    
    // Calculate weighted average of changes
    const total = changes.reduce((sum, change, index) => {
      const weight = (index + 1) / changes.length;
      return sum + (change * weight);
    }, 0);
    
    return Math.min(100, Math.max(-100, total));
  }
}

export default MetaTracker;