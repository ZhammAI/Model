// src/services/marketSentiment.js

class MarketSentiment {
  constructor() {
    this.fearGreedIndex = 50; // Neutral by default
    this.metrics = {
      volatility: 0,
      marketMomentum: 0,
      socialMediaSentiment: 0,
      tokenDominance: 0,
      newTokens: 0
    };
  }

  // Calculate Fear and Greed Index (0-100)
  // 0-25: Extreme Fear
  // 26-45: Fear
  // 46-55: Neutral
  // 56-75: Greed
  // 76-100: Extreme Greed
  calculateFearGreedIndex(marketData) {
    // Update individual metrics
    this.updateVolatility(marketData.priceChanges);
    this.updateMarketMomentum(marketData.volume24h);
    this.updateSocialSentiment(marketData.socialMetrics);
    this.updateTokenDominance(marketData.topTokens);
    this.updateNewTokens(marketData.tokenCreation);

    // Calculate weighted average
    const weights = {
      volatility: 0.25,
      marketMomentum: 0.25,
      socialMediaSentiment: 0.2,
      tokenDominance: 0.15,
      newTokens: 0.15
    };

    let weightedSum = 0;
    Object.keys(this.metrics).forEach(metric => {
      weightedSum += this.metrics[metric] * weights[metric];
    });

    this.fearGreedIndex = Math.round(weightedSum);
    return this.getIndexData();
  }

  // Get formatted index data with classification
  getIndexData() {
    return {
      value: this.fearGreedIndex,
      classification: this.classifyIndex(),
      metrics: this.metrics
    };
  }

  // Classify the current index value
  classifyIndex() {
    if (this.fearGreedIndex <= 25) return 'Extreme Fear';
    if (this.fearGreedIndex <= 45) return 'Fear';
    if (this.fearGreedIndex <= 55) return 'Neutral';
    if (this.fearGreedIndex <= 75) return 'Greed';
    return 'Extreme Greed';
  }

  // Update individual metrics

  updateVolatility(priceChanges) {
    // Calculate volatility based on price movements
    const volatility = Math.abs(priceChanges.reduce((acc, change) => acc + change, 0) / priceChanges.length);
    this.metrics.volatility = this.normalizeMetric(volatility, 0, 30);
  }

  updateMarketMomentum(volume24h) {
    // Compare current volume to moving average
    const volumeChange = (volume24h.current - volume24h.average) / volume24h.average * 100;
    this.metrics.marketMomentum = this.normalizeMetric(volumeChange, -50, 50);
  }

  updateSocialSentiment(socialMetrics) {
    // Analyze social media sentiment
    const sentiment = (socialMetrics.positive - socialMetrics.negative) / socialMetrics.total * 100;
    this.metrics.socialMediaSentiment = this.normalizeMetric(sentiment, -100, 100);
  }

  updateTokenDominance(topTokens) {
    // Calculate market concentration
    const dominance = topTokens.slice(0, 10).reduce((acc, token) => acc + token.marketShare, 0);
    this.metrics.tokenDominance = this.normalizeMetric(dominance, 20, 80);
  }

  updateNewTokens(tokenCreation) {
    // Analyze new token creation rate
    const creationRate = (tokenCreation.current - tokenCreation.average) / tokenCreation.average * 100;
    this.metrics.newTokens = this.normalizeMetric(creationRate, -50, 50);
  }

  // Normalize metric to 0-100 scale
  normalizeMetric(value, min, max) {
    return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  }
}

export default MarketSentiment;