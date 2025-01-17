// src/utils/helpers.js

import { TOKEN_METRICS, TIME_CONSTANTS, WALLET_TYPES } from './constants';

/**
 * Format number to compact representation
 * @param {number} num - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '0';
  
  const lookup = [
    { value: 1e9, symbol: 'B' },
    { value: 1e6, symbol: 'M' },
    { value: 1e3, symbol: 'K' },
    { value: 1, symbol: '' }
  ];

  const item = lookup.find(item => Math.abs(num) >= item.value) || lookup[lookup.length - 1];
  return (num / item.value).toFixed(decimals) + item.symbol;
};

/**
 * Calculate percentage change between two values
 * @param {number} current - Current value
 * @param {number} previous - Previous value
 * @returns {number} Percentage change
 */
export const calculatePercentageChange = (current, previous) => {
  if (!previous) return 0;
  return ((current - previous) / previous) * 100;
};

/**
 * Format timestamp to relative time
 * @param {number} timestamp - Unix timestamp
 * @returns {string} Relative time string
 */
export const formatTimeAgo = (timestamp) => {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);

  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };

  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval}${unit.charAt(0)}`;
    }
  }
  return 'now';
};

/**
 * Validate token metrics against minimum requirements
 * @param {Object} token - Token data
 * @returns {boolean} Whether token meets requirements
 */
export const validateTokenMetrics = (token) => {
  const age = Date.now() - token.createdAt;
  
  return (
    token.liquidityUSD >= TOKEN_METRICS.MIN_LIQUIDITY_USD &&
    token.holders >= TOKEN_METRICS.MIN_HOLDERS &&
    age <= TIME_CONSTANTS.ONE_WEEK &&
    token.volume24h >= TOKEN_METRICS.MIN_VOLUME_USD &&
    token.marketCap >= TOKEN_METRICS.MIN_MARKET_CAP
  );
};

/**
 * Classify wallet based on holding size
 * @param {number} holdingValue - Value of holdings in USD
 * @returns {string} Wallet classification
 */
export const classifyWallet = (holdingValue) => {
  if (holdingValue >= 50000) return WALLET_TYPES.WHALE;
  if (holdingValue >= 10000) return WALLET_TYPES.MEDIUM;
  if (holdingValue >= 1000) return WALLET_TYPES.SMALL;
  return WALLET_TYPES.DUST;
};

/**
 * Calculate exponential moving average
 * @param {Array} data - Array of numbers
 * @param {number} periods - Number of periods
 * @returns {number} EMA value
 */
export const calculateEMA = (data, periods) => {
  const k = 2 / (periods + 1);
  let ema = data[0];
  
  for (let i = 1; i < data.length; i++) {
    ema = data[i] * k + ema * (1 - k);
  }
  
  return ema;
};

/**
 * Check if token name/symbol contains trending keywords
 * @param {string} text - Text to check
 * @param {Array} keywords - Keywords to look for
 * @returns {Array} Matched keywords
 */
export const findMatchingKeywords = (text, keywords) => {
  const normalizedText = text.toLowerCase();
  return keywords.filter(keyword => 
    normalizedText.includes(keyword.toLowerCase())
  );
};

/**
 * Format wallet address to shortened form
 * @param {string} address - Wallet address
 * @returns {string} Shortened address
 */
export const formatAddress = (address) => {
  if (!address) return '';
  return `${address.slice(0, 4)}...${address.slice(-4)}`;
};

/**
 * Calculate volume health score
 * @param {Object} token - Token data
 * @returns {number} Health score (0-100)
 */
export const calculateVolumeHealth = (token) => {
  const volumeToMcap = token.volume24h / token.marketCap;
  const liquidityToMcap = token.liquidityUSD / token.marketCap;
  
  // Score different metrics
  const volumeScore = Math.min(volumeToMcap * 100, 50);
  const liquidityScore = Math.min(liquidityToMcap * 100, 30);
  const holdersScore = Math.min((token.holders / 1000) * 20, 20);
  
  return Math.round(volumeScore + liquidityScore + holdersScore);
};

/**
 * Check if token is potentially a honeypot
 * @param {Object} token - Token data
 * @returns {boolean} Whether token might be a honeypot
 */
export const isHoneypotSuspect = (token) => {
  const sellTax = token.sellTax || 0;
  const buyTax = token.buyTax || 0;
  const maxTxAmount = token.maxTxAmount || token.totalSupply;
  
  return (
    sellTax > 10 ||
    buyTax > 10 ||
    maxTxAmount < (token.totalSupply * 0.001) ||
    token.liquidityUSD < TOKEN_METRICS.MIN_LIQUIDITY_USD
  );
};