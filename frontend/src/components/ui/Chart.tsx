import React from 'react';

interface ChartProps {
  data: Array<{ label: string; value: number; color?: string }>;
  type?: 'bar' | 'line' | 'pie' | 'doughnut';
  height?: number;
  className?: string;
}

const Chart: React.FC<ChartProps> = ({ 
  data, 
  type = 'bar', 
  height = 300, 
  className = '' 
}) => {
  // Handle empty data gracefully
  if (!data || data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height }}>
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }
  
  const maxValue = Math.max(...data.map(d => d.value));
  
  if (type === 'bar') {
    return (
      <div className={`space-y-2 ${className}`} style={{ height: `${height}px` }}>
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className="w-20 text-sm text-gray-600 truncate">
              {item.label}
            </div>
            <div className="flex-1 bg-gray-200 rounded-full h-6">
              <div
                className="h-6 rounded-full transition-all duration-300"
                style={{
                  width: `${(item.value / maxValue) * 100}%`,
                  backgroundColor: item.color || '#3B82F6'
                }}
              />
            </div>
            <div className="w-12 text-sm font-medium text-gray-900 text-right">
              {item.value}
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  if (type === 'line') {
    return (
      <div className={`relative ${className}`} style={{ height: `${height}px` }}>
        <svg width="100%" height="100%" className="overflow-visible">
          <polyline
            fill="none"
            stroke="#3B82F6"
            strokeWidth="2"
            points={data.map((item, index) => 
              `${(index / (data.length - 1)) * 100},${100 - (item.value / maxValue) * 100}`
            ).join(' ')}
          />
          {data.map((item, index) => (
            <circle
              key={index}
              cx={`${(index / (data.length - 1)) * 100}%`}
              cy={`${100 - (item.value / maxValue) * 100}%`}
              r="4"
              fill="#3B82F6"
            />
          ))}
        </svg>
      </div>
    );
  }
  
  if (type === 'pie' || type === 'doughnut') {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;
    
    return (
      <div className={`relative ${className}`} style={{ height: `${height}px` }}>
        <svg width="100%" height="100%" viewBox="0 0 100 100">
          {data.map((item, index) => {
            const percentage = item.value / total;
            const startAngle = currentAngle;
            const endAngle = currentAngle + percentage * 360;
            currentAngle = endAngle;
            
            const startRadians = (startAngle - 90) * Math.PI / 180;
            const endRadians = (endAngle - 90) * Math.PI / 180;
            
            const x1 = 50 + 40 * Math.cos(startRadians);
            const y1 = 50 + 40 * Math.sin(startRadians);
            const x2 = 50 + 40 * Math.cos(endRadians);
            const y2 = 50 + 40 * Math.sin(endRadians);
            
            const largeArcFlag = percentage > 0.5 ? 1 : 0;
            
            return (
              <path
                key={index}
                d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                fill={item.color || `hsl(${(index * 137.5) % 360}, 70%, 60%)`}
              />
            );
          })}
          {type === 'doughnut' && (
            <circle cx="50" cy="50" r="25" fill="white" />
          )}
        </svg>
      </div>
    );
  }
  
  return null;
};

export default Chart;
