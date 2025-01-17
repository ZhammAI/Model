// src/hooks/useWebSocket.js

import { useState, useEffect, useCallback } from 'react';
import wsService from '../services/websocket';

const useWebSocket = () => {
  const [connectionStatus, setConnectionStatus] = useState(wsService.getStatus());
  const [metaData, setMetaData] = useState({
    trending: [],
    rising: [],
    declining: [],
    lastUpdate: null
  });
  const [marketSentiment, setMarketSentiment] = useState({
    value: 50,
    classification: 'Neutral',
    metrics: {},
    lastUpdate: null
  });
  const [runners, setRunners] = useState({
    current: [],
    potential: [],
    lastUpdate: null
  });
  const [error, setError] = useState(null);

  // Handle meta updates
  const handleMetaUpdate = useCallback((data) => {
    setMetaData(prev => ({
      ...prev,
      ...data,
      lastUpdate: new Date()
    }));
  }, []);

  // Handle sentiment updates
  const handleSentimentUpdate = useCallback((data) => {
    setMarketSentiment(prev => ({
      ...prev,
      ...data,
      lastUpdate: new Date()
    }));
  }, []);

  // Handle runners updates
  const handleRunnersUpdate = useCallback((data) => {
    setRunners(prev => ({
      ...prev,
      ...data,
      lastUpdate: new Date()
    }));
  }, []);

  // Handle connection status
  const handleConnectionUpdate = useCallback((data) => {
    setConnectionStatus(data.status);
    if (data.status === 'connected') {
      setError(null);
    }
  }, []);

  // Handle errors
  const handleError = useCallback((data) => {
    setError(data.error);
    console.error('WebSocket error:', data.error);
  }, []);

  // Initialize WebSocket connection and subscribers
  useEffect(() => {
    wsService.connect();

    const subscriptions = [
      wsService.subscribe('meta_update', handleMetaUpdate),
      wsService.subscribe('sentiment_update', handleSentimentUpdate),
      wsService.subscribe('runners_update', handleRunnersUpdate),
      wsService.subscribe('connection', handleConnectionUpdate),
      wsService.subscribe('error', handleError)
    ];

    // Cleanup subscriptions
    return () => {
      subscriptions.forEach(unsubscribe => unsubscribe());
    };
  }, [
    handleMetaUpdate,
    handleSentimentUpdate,
    handleRunnersUpdate,
    handleConnectionUpdate,
    handleError
  ]);

  // Send message helper
  const sendMessage = useCallback((type, payload) => {
    return wsService.sendMessage(type, payload);
  }, []);

  // Request data refresh
  const refreshData = useCallback(() => {
    sendMessage('refresh_request', {
      timestamp: new Date().toISOString()
    });
  }, [sendMessage]);

  // Reconnect helper
  const reconnect = useCallback(() => {
    wsService.connect();
  }, []);

  // Disconnect helper
  const disconnect = useCallback(() => {
    wsService.disconnect();
  }, []);

  return {
    // State
    connectionStatus,
    metaData,
    marketSentiment,
    runners,
    error,

    // Actions
    sendMessage,
    refreshData,
    reconnect,
    disconnect,

    // Computed
    isConnected: connectionStatus === 'connected',
    isConnecting: connectionStatus === 'connecting',
    hasError: !!error
  };
};

export default useWebSocket;

/* Example usage:
import useWebSocket from './hooks/useWebSocket';

const MyComponent = () => {
  const {
    connectionStatus,
    metaData,
    marketSentiment,
    runners,
    error,
    refreshData,
    isConnected
  } = useWebSocket();

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <div>Status: {connectionStatus}</div>
      <button 
        onClick={refreshData}
        disabled={!isConnected}
      >
        Refresh Data
      </button>
      
      {metaData.trending.map(trend => (
        <div key={trend.name}>
          {trend.name}: {trend.percentage}%
        </div>
      ))}
    </div>
  );
};
*/