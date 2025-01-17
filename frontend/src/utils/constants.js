// src/utils/constants.js

// Meta Categories and Keywords
export const META_CATEGORIES = {
  TRENDING: 'trending',
  RISING: 'rising',
  DECLINING: 'declining'
};

// Common metas to track
export const COMMON_METAS = [
  'ai',
  'new',
  'squid',
  'agent',
  'game',
  'mascot',
  'live',
  'sol',
  'year'
];

// Market Sentiment Thresholds
export const SENTIMENT_THRESHOLDS = {
  EXTREME_FEAR: 25,
  FEAR: 45,
  NEUTRAL: 55,
  GREED: 75,
  EXTREME_GREED: 100
};

// Token Analysis Parameters
export const TOKEN_METRICS = {
  MIN_LIQUIDITY_USD: 10000,
  MIN_HOLDERS: 100,
  MAX_AGE_DAYS: 7,
  MIN_VOLUME_USD: 5000,
  MIN_MARKET_CAP: 50000
};

// Time Constants (in milliseconds)
export const TIME_CONSTANTS = {
  ONE_MINUTE: 60 * 1000,
  FIVE_MINUTES: 5 * 60 * 1000,
  ONE_HOUR: 60 * 60 * 1000,
  ONE_DAY: 24 * 60 * 60 * 1000,
  ONE_WEEK: 7 * 24 * 60 * 60 * 1000
};

// API Endpoints
export const API_ENDPOINTS = {
  SOLANA_RPC: 'https://api.mainnet-beta.solana.com',
  JUPITER_API: 'https://price.jup.ag/v4',
  BIRDEYE_API: 'https://public-api.birdeye.so'
};

// Error Messages
export const ERROR_MESSAGES = {
  FETCH_FAILED: 'Failed to fetch data',
  INVALID_TOKEN: 'Invalid token address',
  NO_LIQUIDITY: 'Insufficient liquidity',
  API_ERROR: 'API request failed',
  RATE_LIMIT: 'Rate limit exceeded'
};

// Wallet Types for tracking holder distribution
export const WALLET_TYPES = {
  WHALE: 'Whale',
  MEDIUM: 'Medium',
  SMALL: 'Small',
  DUST: 'Dust'
};

// Market Status Classifications
export const MARKET_STATUS = {
  BULL: 'Bull Market',
  BEAR: 'Bear Market',
  CONSOLIDATION: 'Consolidation',
  RECOVERY: 'Recovery'
};

// Color schemes for UI components
export const COLORS = {
  SENTIMENT: {
    EXTREME_FEAR: '#ff4444',
    FEAR: '#ff8c00',
    NEUTRAL: '#ffeb3b',
    GREED: '#4caf50',
    EXTREME_GREED: '#2e7d32'
  },
  PRICE_CHANGE: {
    POSITIVE: '#4caf50',
    NEGATIVE: '#f44336',
    NEUTRAL: '#9e9e9e'
  }
};