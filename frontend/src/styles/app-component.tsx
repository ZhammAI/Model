import React, { createContext, useContext, useEffect, useState } from 'react';

// WebSocket Service
const wsService = {
  ws: null,
  url: `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/meta`,
  connect() {
    this.ws = new WebSocket(this.url);
    return this.ws;
  }
};

// Create Meta Context
const MetaContext = createContext(null);

// Meta Provider Component
const MetaProvider = ({ children }) => {
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
    const ws = wsService.connect();

    ws.onopen = () => {
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'meta_update':
          setMetaState(prev => ({
            ...prev,
            ...data.payload,
            isLoading: false
          }));
          break;
        case 'sentiment_update':
          setMarketSentiment(prev => ({
            ...prev,
            ...data.payload
          }));
          break;
        case 'runners_update':
          setRunners(prev => ({
            ...prev,
            ...data.payload
          }));
          break;
        default:
          break;
      }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
    };

    return () => {
      ws.close();
    };
  }, []);

  const value = {
    meta: metaState,
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

// Custom hook for using meta context
const useMeta = () => {
  const context = useContext(MetaContext);
  if (!context) {
    throw new Error('useMeta must be used within a MetaProvider');
  }
  return context;
};

// Dashboard Component
const Dashboard = () => {
  const { meta, sentiment, runners } = useMeta();

  if (meta.isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-lg">Loading market data...</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Meta Trends */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Meta Trends</h2>
        <div className="space-y-4">
          {meta.trending.map((trend, index) => (
            <div key={index} className="flex justify-between items-center">
              <span>{trend.name}</span>
              <span className="text-green-400">{trend.percentage.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Market Sentiment */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Market Sentiment</h2>
        <div className="text-2xl font-bold text-center mb-4">
          {sentiment.classification}
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4">
          <div
            className="bg-green-500 h-4 rounded-full"
            style={{ width: `${sentiment.value}%` }}
          />
        </div>
      </div>

      {/* Current Runners */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Current Runners</h2>
        <div className="space-y-4">
          {runners.current.map((runner, index) => (
            <div key={index} className="flex justify-between items-center">
              <span>{runner.name}</span>
              <span className="text-green-400">+{runner.priceChange}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Potential Runners */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Potential Runners</h2>
        <div className="space-y-4">
          {runners.potential.map((runner, index) => (
            <div key={index} className="flex justify-between items-center">
              <span>{runner.name}</span>
              <span className="text-blue-400">{runner.matchedMeta.join(', ')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Connection Status Component
const ConnectionStatus = () => {
  const { connectionStatus } = useMeta();
  
  return (
    <div className="flex items-center space-x-2">
      <div 
        className={`w-2 h-2 rounded-full ${
          connectionStatus === 'connected' 
            ? 'bg-green-500' 
            : 'bg-red-500'
        }`} 
      />
      <span className="text-sm text-gray-400">
        {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
};

// Social Links Component
const SocialLinks = () => {
  const links = [
    { name: 'Twitter', href: 'https://twitter.com/zham_ai' },
    { name: 'Discord', href: 'https://discord.gg/zham-ai' },
    { name: 'Telegram', href: 'https://t.me/zham_ai' }
  ];

  return (
    <>
      {links.map((link) => (
        <a
          key={link.name}
          href={link.href}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-300 transition-colors"
        >
          {link.name}
        </a>
      ))}
    </>
  );
};

// Main App Component
const App = () => {
  return (
    <MetaProvider>
      <div className="min-h-screen bg-gray-900 text-white">
        {/* Header */}
        <header className="border-b border-gray-800">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                  Zham AI
                </h1>
              </div>
              <ConnectionStatus />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Dashboard />
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 mt-auto">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center text-sm text-gray-500">
              <div>
                © {new Date().getFullYear()} Zham AI - Solana Memecoin Tracker
              </div>
              <div className="flex space-x-4">
                <SocialLinks />
              </div>
            </div>
          </div>
        </footer>
      </div>
    </MetaProvider>
  );
};

export default App;