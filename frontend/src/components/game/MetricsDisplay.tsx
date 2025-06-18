import React from 'react';

interface MetricsDisplayProps {
  money: number;
  reputation: number;
  inventory: number;
}

export const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ 
  money, 
  reputation, 
  inventory 
}) => {
  // 백만원 단위로 변환 (소수점 1자리까지)
  const formatMoney = (amount: number) => {
    return `${(amount / 1000000).toFixed(1)}백만원`;
  };

  return (
    <div className="space-y-4">
      <h2 className="text-game-accent font-game text-lg">📊 경영 현황</h2>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-game-text">💰</span>
          <span className="text-game-text font-bold">{formatMoney(money)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-game-text">⭐</span>
          <span className="text-game-text font-bold">{reputation}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-game-text">📦</span>
          <span className="text-game-text font-bold">{inventory}</span>
        </div>
      </div>
    </div>
  );
}; 