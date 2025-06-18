import React, { useState } from 'react';
import { StatusBar } from '@/components/ui/StatusBar';
import { MetricsDisplay } from '@/components/game/MetricsDisplay';
import { ActionBar } from '@/components/layout/ActionBar';

export default function Home() {
  // 임시 상태 (나중에 백엔드와 연동)
  const [gameState] = useState({
    money: 100500000, // 100.5백만원
    reputation: 80,
    inventory: 50,
    happiness: 75,
    fatigue: 30,
  });

  const actions = [
    {
      id: 'prepare',
      icon: '📦',
      label: '재료준비',
      duration: '2h',
      tooltipContent: (
        <div>
          <div className="font-bold mb-2">재료준비 (2시간)</div>
          <div className="text-sm">
            <div>▶ 효과</div>
            <div className="ml-2">• 재고 +30</div>
            <div className="ml-2">• 피로도 +10</div>
            <div>▶ 필요 자원</div>
            <div className="ml-2">• 3.5백만원</div>
          </div>
        </div>
      ),
      onClick: () => console.log('재료준비'),
    },
    {
      id: 'promote',
      icon: '📢',
      label: '홍보활동',
      duration: '2h',
      tooltipContent: (
        <div>
          <div className="font-bold mb-2">홍보활동 (2시간)</div>
          <div className="text-sm">
            <div>▶ 효과</div>
            <div className="ml-2">• 평판 +5</div>
            <div className="ml-2">• 피로도 +15</div>
            <div>▶ 필요 자원</div>
            <div className="ml-2">• 1.2백만원</div>
          </div>
        </div>
      ),
      onClick: () => console.log('홍보활동'),
    },
    {
      id: 'maintain',
      icon: '🔧',
      label: '시설점검',
      duration: '1h',
      tooltipContent: (
        <div>
          <div className="font-bold mb-2">시설점검 (1시간)</div>
          <div className="text-sm">
            <div>▶ 효과</div>
            <div className="ml-2">• 시설 상태 +20</div>
            <div className="ml-2">• 피로도 +5</div>
          </div>
        </div>
      ),
      onClick: () => console.log('시설점검'),
    },
  ];

  return (
    <div className="min-h-screen bg-game-primary text-game-text">
      {/* 헤더 */}
      <header className="p-4 border-b border-game-accent">
        <div className="flex justify-between items-center">
          <div>📅 3일차 [🕐 13:45] (영업중)</div>
          <div className="flex gap-4">
            <button>🔔</button>
            <button>⚙️</button>
            <button>🌙</button>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <div className="flex h-[calc(100vh-8rem)]">
        {/* 왼쪽 사이드바 */}
        <div className="w-64 p-4 border-r border-game-accent">
          <MetricsDisplay
            money={gameState.money}
            reputation={gameState.reputation}
            inventory={gameState.inventory}
          />
          
          <div className="mt-8">
            <h2 className="text-game-accent font-game text-lg mb-4">👤 상태</h2>
            <div className="space-y-4">
              <StatusBar
                type="happiness"
                value={gameState.happiness}
                icon="😊"
                tooltipContent={
                  <div>
                    <div className="font-bold mb-2">행복도</div>
                    <div>현재: {gameState.happiness}/100</div>
                    <div className="mt-2">증가 요인:</div>
                    <div className="ml-2">• 매출 상승 (+5)</div>
                    <div className="ml-2">• 단골 증가 (+3)</div>
                    <div className="mt-2">감소 요인:</div>
                    <div className="ml-2">• 피로 누적 (-2)</div>
                  </div>
                }
              />
              <StatusBar
                type="fatigue"
                value={gameState.fatigue}
                icon="😴"
                tooltipContent={
                  <div>
                    <div className="font-bold mb-2">피로도</div>
                    <div>현재: {gameState.fatigue}/100</div>
                    <div className="mt-2">누적 요인:</div>
                    <div className="ml-2">• 장시간 근무 (+15)</div>
                    <div className="ml-2">• 스트레스 (+5)</div>
                    <div className="mt-2">회복 필요:</div>
                    <div className="ml-2">• 4시간 휴식 시 -30</div>
                    <div className="ml-2">• 8시간 휴식 시 -60</div>
                  </div>
                }
              />
            </div>
          </div>
        </div>

        {/* 메인 영역 */}
        <div className="flex-1 p-4">
          <div className="h-full border border-game-accent rounded p-4">
            스토리텔링 영역
          </div>
        </div>

        {/* 오른쪽 사이드바 */}
        <div className="w-64 p-4 border-l border-game-accent">
          <div>
            <h2 className="text-game-accent font-game text-lg mb-4">📋 최근 이벤트</h2>
            <div className="space-y-2">
              <div>• 단골손님 방문 (+평판 5)</div>
              <div>• 재료값 상승 (-3.2백만원)</div>
              <div>• 신규 손님 증가</div>
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-game-accent font-game text-lg mb-4">🕒 진행중인 효과</h2>
            <div className="space-y-2">
              <div>• ⚡ 전기세 20% 할인 (2일 남음)</div>
              <div>• 🌶️ 매운맛 선호도 증가 (1일)</div>
              <div>• 🚗 배달 시간 10% 감소 (3시간)</div>
            </div>
          </div>
        </div>
      </div>

      {/* 하단 액션바 */}
      <ActionBar actions={actions} />
    </div>
  );
} 