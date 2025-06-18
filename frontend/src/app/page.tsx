import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-center">치킨마스터</h1>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 경영 현황 섹터 */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">경영 현황</h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400">자금</p>
                <p className="text-2xl font-bold">100.5백만원</p>
              </div>
              <div>
                <p className="text-gray-400">평판</p>
                <p className="text-2xl font-bold">85/100</p>
              </div>
              <div>
                <p className="text-gray-400">재고</p>
                <p className="text-2xl font-bold">75%</p>
              </div>
            </div>
          </div>

          {/* 상태 섹터 */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">상태</h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400">행복도</p>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '70%' }}></div>
                </div>
              </div>
              <div>
                <p className="text-gray-400">피로도</p>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div className="bg-red-600 h-2.5 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* 시간 섹터 */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">시간</h2>
            <div className="text-center">
              <p className="text-3xl font-bold">14:30</p>
              <p className="text-gray-400 mt-2">영업 시간: 12:00 - 22:00</p>
            </div>
          </div>
        </div>

        {/* 액션 버튼 */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            주문 받기
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            재료 준비
          </button>
          <button className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            재고 관리
          </button>
          <button className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            휴식
          </button>
        </div>

        {/* 이벤트 로그 */}
        <div className="mt-8 bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">이벤트 로그</h2>
          <div className="space-y-2 text-sm">
            <p>14:30 - 신규 주문이 들어왔습니다: 후라이드 치킨 2마리</p>
            <p>14:25 - 양념 치킨 조리가 완료되었습니다</p>
            <p>14:20 - 재료 준비를 시작했습니다</p>
          </div>
        </div>
      </div>
    </main>
  )
}
