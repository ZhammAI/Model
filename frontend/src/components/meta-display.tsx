import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const MetaDisplay = ({ metaData }) => {
  // Example meta data structure
  const defaultMetaData = {
    trending: [
      { name: 'ai', percentage: 91.9 },
      { name: 'new', percentage: 24.0 },
      { name: 'squid', percentage: 11.2 },
      { name: 'agent', percentage: 9.6 },
      { name: 'game', percentage: 8.7 }
    ],
    rising: [
      { name: 'mascot', percentage: 8.1 },
      { name: 'live', percentage: 7.5 },
      { name: 'sol', percentage: 6.8 },
      { name: 'year', percentage: 5.9 }
    ],
    declining: []
  };

  const data = metaData || defaultMetaData;

  const renderMetaSection = (title, items, emoji) => (
    <div className="space-y-2">
      <div className="flex items-center space-x-2">
        <span className="text-lg">{emoji}</span>
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      {items.map((item, index) => (
        <div key={index} className="flex items-center space-x-2">
          <div className="w-32 bg-gray-200 rounded-full h-4">
            <div
              className="bg-purple-600 h-4 rounded-full"
              style={{ width: `${item.percentage}%` }}
            />
          </div>
          <span className="text-sm">
            {item.name}: {item.percentage}%
          </span>
        </div>
      ))}
    </div>
  );

  return (
    <Card className="w-full max-w-md bg-gray-900 text-white">
      <CardHeader>
        <CardTitle>Current PF Metas</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {renderMetaSection('Top Trending', data.trending, '🔥')}
        {renderMetaSection('Rising', data.rising, '📈')}
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-lg">📉</span>
            <h3 className="text-lg font-semibold">Declining</h3>
          </div>
          {data.declining.length === 0 ? (
            <p className="text-gray-400">No declining metas.</p>
          ) : (
            renderMetaSection('Declining', data.declining, '📉')
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MetaDisplay;