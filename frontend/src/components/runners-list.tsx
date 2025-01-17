import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpCircle, TrendingUp, DollarSign } from 'lucide-react';

const RunnersList = ({ title, runners, className }) => {
  if (!runners || runners.length === 0) {
    return (
      <Card className={`w-full ${className}`}>
        <CardHeader>
          <CardTitle className="text-white">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">No runners found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          {title === "Current Runners" ? (
            <TrendingUp className="h-5 w-5" />
          ) : (
            <ArrowUpCircle className="h-5 w-5" />
          )}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {runners.map((runner, index) => (
            <div 
              key={index}
              className="bg-gray-800 rounded-lg p-4 flex justify-between items-center"
            >
              <div className="flex flex-col">
                <span className="text-white font-semibold">{runner.name}</span>
                <span className="text-sm text-gray-400">
                  {runner.matchedMeta.join(', ')}
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex flex-col items-end">
                  <span className="text-green-400 font-semibold">
                    ${runner.price.toFixed(6)}
                  </span>
                  <span className={`text-sm ${
                    runner.priceChange >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {runner.priceChange >= 0 ? '+' : ''}{runner.priceChange}%
                  </span>
                </div>
                <DollarSign className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default RunnersList;