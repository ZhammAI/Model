// frontend/src/context/MetaContext.jsx

import React, { createContext, useContext, useEffect, useState } from 'react';
import wsService from '../services/websocket';

const MetaContext = createContext();

export const MetaProvider = ({ children }) => {
  const [metaState, setMetaState] = useState({
    trending: [],
    rising: [],
    declining: [],
    isLoading: true,
    error: null
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

  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    // Initialize WebSocket connection
    wsService.connect();

    // Subscribe to WebSocket events
    const subscriptions = [
      wsService.subscribe('meta_update', handleMetaUpdate),
      wsService.subscribe('sentiment_update', handleSentimentUpdate),
      wsService.subscribe('runners_update', handleRunnersUpdate),
      wsService.subscribe('connection', handleConnectionUpdate),
      wsService.subscribe('error', handleError)
    ];

    // Cleanup subscriptions on unmount
    return () => {
      subscriptions.forEach(unsubscribe => unsubscribe());
      wsService.disconnect();
    };
  }, []);

  const handleMetaUpdate = (data) => {
    setMetaState(prev => ({
      ...prev,
      ...data,
      isLoading: false,
      error: null,
      lastUpdate: new Date()
    }));
  };

  const handleSentimentUpdate = (data) => {
    setMarketSentiment(prev => ({
      ...prev,
      ...data,
      lastUpdate: new Date()
    }));
  };

  const handleRunnersUpdate = (data) => {
    setRunners(prev => ({
      ...prev,
      ...data,
      lastUpdate: new Date()
    }));
  };

  const handleConnectionUpdate = (data) => {
    setConnectionStatus(data.status);
    if (data.status === 'disconnected') {
      setMetaState(prev => ({ ...prev, isLoading: true }));
    }
  };

  const handleError = (data) => {
    setMetaState(prev => ({
      ...prev,
      error: data.error,
      isLoading: false
    }));
    console.error('Meta context error:', data.error);
  };

  const refreshData = () => {
    setMetaState(prev => ({ ...prev, isLoading: true }));
    wsService.sendMessage('refresh_request', { timestamp: new Date() });
  };

  const value = {
    meta: {
      ...metaState,
      refresh: refreshData
    },
    sentiment: marketSentiment,
    runners,
    connectionStatus
  };

  return (
    <MetaContext.Provider value={value}>
      {children}
    </MetaContext.Provider>
  );
};

// Custom hook to use the meta context
export const useMeta = () => {
  const context = useContext(MetaContext);
  if (!context) {
    throw new Error('useMeta must be used within a MetaProvider');
  }
  return context;
};

// Example usage in App.jsx:
/*
import { MetaProvider } from './context/MetaContext';

function App() {
  return (
    <MetaProvider>
      <Dashboard />
    </MetaProvider>
  );
}
*/

// Example usage in a component:
/*
function MetaDisplay() {
  const { meta, sentiment, runners } = useMeta();

  if (meta.isLoading) {
    return <div>Loading...</div>;
  }

  if (meta.error) {
    return <div>Error: {meta.error}</div>;
  }

  return (
    <div>
      <h2>Trending Metas</h2>
      {meta.trending.map(item => (
        <div key={item.name}>{item.name}: {item.percentage}%</div>
      ))}
      
      <h2>Market Sentiment</h2>
      <div>{sentiment.classification} ({sentiment.value})</div>
      
      <h2>Current Runners</h2>
      {runners.current.map(runner => (
        <div key={runner.name}>{runner.name}</div>
      ))}
    </div>
  );
}
*/