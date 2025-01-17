// src/services/tokenAnalyzer.js

class TokenAnalyzer {
  constructor() {
    this.currentMeta = new Map();
    this.runners = new Set();
    this.potentialRunners = new Set();
  }

  // Update meta trends based on new token data
  updateMetaTrends(tokenData) {
    const trends = new Map();
    
    // Analyze token names and descriptions for meta keywords
    tokenData.forEach(token => {
      const keywords = this.extractKeywords(token.name, token.description);
      keywords.forEach(keyword => {
        const count = trends.get(keyword) || 0;
        trends.set(keyword, count + token.volume);
      });
    });

    // Calculate percentages
    const totalVolume = Array.from(trends.values()).reduce((a, b) => a + b, 0);
    const metaPercentages = new Map();
    
    trends.forEach((volume, keyword) => {
      const percentage = (volume / totalVolume) * 100;
      metaPercentages.set(keyword, percentage);
    });

    this.currentMeta = metaPercentages;
    return this.formatMetaData();
  }

  // Extract relevant keywords from token name and description
  extractKeywords(name, description) {
    const combined = `${name} ${description}`.toLowerCase();
    const keywords = new Set();

    // Add your keyword detection logic here
    const commonMetas = ['ai', 'new', 'squid', 'agent', 'game', 'mascot', 'live', 'sol', 'year'];
    commonMetas.forEach(meta => {
      if (combined.includes(meta)) {
        keywords.add(meta);
      }
    });

    return keywords;
  }

  // Format meta data for display
  formatMetaData() {
    const sortedMetas = Array.from(this.currentMeta.entries())
      .sort((a, b) => b[1] - a[1]);

    return {
      trending: sortedMetas.slice(0, 5).map(([name, percentage]) => ({
        name,
        percentage: parseFloat(percentage.toFixed(1))
      })),
      rising: sortedMetas.slice(5, 9).map(([name, percentage]) => ({
        name,
        percentage: parseFloat(percentage.toFixed(1))
      })),
      declining: []  // Implement decline detection logic
    };
  }

  // Analyze potential runners based on meta trends
  analyzePotentialRunners(tokens) {
    const potentialRunners = new Set();
    const topMetas = Array.from(this.currentMeta.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([keyword]) => keyword);

    tokens.forEach(token => {
      const keywords = this.extractKeywords(token.name, token.description);
      const matchesTopMeta = topMetas.some(meta => keywords.has(meta));
      const hasGoodMetrics = this.checkTokenMetrics(token);

      if (matchesTopMeta && hasGoodMetrics) {
        potentialRunners.add(token);
      }
    });

    this.potentialRunners = potentialRunners;
    return Array.from(potentialRunners);
  }

  // Check token metrics (customize based on your criteria)
  checkTokenMetrics(token) {
    return (
      token.liquidityUSD > 10000 &&  // Minimum liquidity
      token.holders > 100 &&         // Minimum holders
      token.createdAt > Date.now() - (7 * 24 * 60 * 60 * 1000) // Within last week
    );
  }
}

export default TokenAnalyzer;