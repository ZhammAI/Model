import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

const FearGreedIndex = ({ data }) => {
  if (!data) {
    return (
      <Card className="w-full bg-gray-900">
        <CardHeader>
          <CardTitle className="text-white">Fear & Greed Index</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">Loading sentiment data...</p>
        </CardContent>
      </Card>
    );
  }

  const getColorClass = (value) => {
    if (value <= 25) return 'bg-red-600';  // Extreme Fear
    if (value <= 45) return 'bg-orange-500';  // Fear
    if (value <= 55) return 'bg-yellow-500';  // Neutral
    if (value <= 75) return 'bg-green-500';  // Greed
    return 'bg-green-600';  // Extreme Greed
  };

  const getIcon = (classification) => {
    switch (classification) {
      case 'Extreme Fear':
      case 'Fear':
        return <TrendingDown className="h-6 w-6 text-red-400" />;
      case 'Neutral':
        return <AlertTriangle className="h-6 w-6 text-yellow-400" />;
      case 'Greed':
      case 'Extreme Greed':
        return <TrendingUp className="h-6 w-6 text-green-400" />;
      default:
        return null;
    }
  };

  return (
    <Card className="w-full bg-gray-900">
      <CardHeader>
        <CardTitle className="text-white">Fear & Greed Index</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getIcon(data.classification)}
              <span className="text-xl font-bold text-white">
                {data.classification}
              </span>
            </div>
            <span className="text-2xl font-bold text-white">
              {data.value}
            </span>
          </div>

          <div className="w-full bg-gray-700 rounded-full h-4">
            <div 
              className={`h-4 rounded-full ${getColorClass(data.value)}`}
              style={{ width: `${data.value}%` }}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {Object.entries(data.metrics).map(([key, value]) => (
              <div key={key} className="bg-gray-800 p-3 rounded-lg">
                <div className="text-sm text-gray-400 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="text-lg font-semibold text-white">
                  {value.toFixed(1)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FearGreedIndex;