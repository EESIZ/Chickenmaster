import React from 'react';
import { Tooltip } from 'react-tooltip';

interface StatusBarProps {
  type: 'happiness' | 'fatigue';
  value: number;
  tooltipContent: React.ReactNode;
  icon: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({ type, value, tooltipContent, icon }) => {
  const barWidth = Math.min(Math.max(value, 0), 100);
  const barColor = type === 'happiness' 
    ? 'bg-game-success' 
    : 'bg-game-warning';

  return (
    <div className="flex items-center gap-2 w-full">
      <span className="text-game-text">{icon}</span>
      <div 
        className="relative w-full h-4 bg-game-secondary rounded"
        data-tooltip-id={`status-${type}`}
      >
        <div 
          className={`h-full ${barColor} rounded transition-all duration-300`}
          style={{ width: `${barWidth}%` }}
        />
      </div>
      <Tooltip
        id={`status-${type}`}
        place="right"
        className="z-50 max-w-xs bg-game-primary border border-game-accent text-game-text p-4 rounded"
      >
        {tooltipContent}
      </Tooltip>
    </div>
  );
}; 