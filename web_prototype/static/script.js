/**
 * 🍗 치킨마스터 웹 게임 JavaScript 🍗
 * 
 * 기존 MUD 게임의 모든 기능을 웹으로 구현
 * FastAPI 백엔드와 통신하여 실시간 게임 플레이 제공
 */

// ===== 전역 변수 =====
let gameState = null;
let previousGameState = null;
let isLoading = false;
let autoRefreshInterval = null;

// API 베이스 URL (개발/배포 환경 자동 감지)
const API_BASE = window.location.origin;

// ===== DOM 요소 캐싱 =====
const elements = {
    // 헤더
    dayDisplay: document.getElementById('dayDisplay'),
    moneyDisplay: document.getElementById('moneyDisplay'),
    
    // 기본 지표
    money: document.getElementById('money'),
    reputation: document.getElementById('reputation'),
    happiness: document.getElementById('happiness'),
    pain: document.getElementById('pain'),
    
    // 운영 지표
    inventory: document.getElementById('inventory'),
    staffFatigue: document.getElementById('staffFatigue'),
    facility: document.getElementById('facility'),
    demand: document.getElementById('demand'),
    
    // 경영 정보
    chickenPrice: document.getElementById('chickenPrice'),
    dailyCustomers: document.getElementById('dailyCustomers'),
    dailyRevenue: document.getElementById('dailyRevenue'),
    
    // 변화량 표시
    moneyChange: document.getElementById('moneyChange'),
    reputationChange: document.getElementById('reputationChange'),
    happinessChange: document.getElementById('happinessChange'),
    painChange: document.getElementById('painChange'),
    inventoryChange: document.getElementById('inventoryChange'),
    staffFatigueChange: document.getElementById('staffFatigueChange'),
    facilityChange: document.getElementById('facilityChange'),
    demandChange: document.getElementById('demandChange'),
    
    // 이벤트 및 메시지
    messageArea: document.getElementById('messageArea'),
    eventsList: document.getElementById('eventsList'),
    
    // 모달
    gameOverModal: document.getElementById('gameOverModal'),
    gameOverReason: document.getElementById('gameOverReason'),
    
    // 로딩
    loadingOverlay: document.getElementById('loadingOverlay')
};

// ===== 유틸리티 함수 =====

/**
 * 숫자를 천 단위 구분자와 함께 포맷팅
 */
function formatNumber(num) {
    return new Intl.NumberFormat('ko-KR').format(Math.floor(num));
}

/**
 * 변화량 표시 (색상 포함)
 */
function formatChange(current, previous) {
    if (previous === undefined || previous === null) return '';
    
    const change = current - previous;
    if (change === 0) return '';
    
    const sign = change > 0 ? '+' : '';
    const className = change > 0 ? 'positive' : 'negative';
    return `<span class="${className}">(${sign}${formatNumber(change)})</span>`;
}

/**
 * 로딩 상태 표시/숨김
 */
function showLoading(show = true) {
    isLoading = show;
    if (elements.loadingOverlay) {
        elements.loadingOverlay.classList.toggle('show', show);
    }
    
    // 모든 버튼 비활성화
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.disabled = show;
        btn.classList.toggle('disabled', show);
    });
}

/**
 * 메시지 표시
 */
function showMessage(text, icon = '💬', type = 'info') {
    if (!elements.messageArea) return;
    
    const messageItem = document.createElement('div');
    messageItem.className = `message-item ${type}`;
    messageItem.innerHTML = `
        <span class="message-icon">${icon}</span>
        <span class="message-text">${text}</span>
    `;
    
    elements.messageArea.appendChild(messageItem);
    
    // 스크롤을 최신 메시지로
    elements.messageArea.scrollTop = elements.messageArea.scrollHeight;
    
    // 메시지가 너무 많으면 오래된 것 제거
    const messages = elements.messageArea.children;
    if (messages.length > 10) {
        elements.messageArea.removeChild(messages[0]);
    }
}

/**
 * 에러 메시지 표시
 */
function showError(message) {
    showMessage(message, '❌', 'error');
    console.error('게임 에러:', message);
}

/**
 * 성공 메시지 표시
 */
function showSuccess(message) {
    showMessage(message, '✅', 'success');
}

// ===== API 통신 함수 =====

/**
 * API 요청 헬퍼
 */
async function apiCall(endpoint, options = {}) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        showError(`API 오류: ${error.message}`);
        throw error;
    } finally {
        showLoading(false);
    }
}

/**
 * 게임 상태 조회
 */
async function fetchGameState() {
    try {
        const data = await apiCall('/api/game/state');
        return data;
    } catch (error) {
        showError('게임 상태를 불러올 수 없습니다.');
        return null;
    }
}

/**
 * 액션 실행
 */
async function executeActionAPI(actionType, parameters = {}) {
    try {
        const data = await apiCall('/api/game/action', {
            method: 'POST',
            body: JSON.stringify({
                action_type: actionType,
                parameters: parameters
            })
        });
        
        return data;
    } catch (error) {
        showError('액션 실행에 실패했습니다.');
        return null;
    }
}

/**
 * 게임 리셋
 */
async function resetGameAPI() {
    try {
        const data = await apiCall('/api/game/reset', {
            method: 'POST'
        });
        
        if (data.success) {
            showSuccess(data.message);
            await refreshGameState();
        }
        
        return data;
    } catch (error) {
        showError('게임 리셋에 실패했습니다.');
        return null;
    }
}

// ===== UI 업데이트 함수 =====

/**
 * 게임 상태 UI 업데이트
 */
function updateGameStateUI(newState) {
    if (!newState) return;
    
    previousGameState = gameState;
    gameState = newState;
    
    // 헤더 업데이트
    if (elements.dayDisplay) elements.dayDisplay.textContent = gameState.day;
    if (elements.moneyDisplay) elements.moneyDisplay.textContent = formatNumber(gameState.money);
    
    // 기본 지표 업데이트
    if (elements.money) elements.money.textContent = `${formatNumber(gameState.money)}원`;
    if (elements.reputation) elements.reputation.textContent = `${Math.floor(gameState.reputation)}점`;
    if (elements.happiness) elements.happiness.textContent = `${Math.floor(gameState.happiness)}점`;
    if (elements.pain) elements.pain.textContent = `${Math.floor(gameState.pain)}점`;
    
    // 운영 지표 업데이트
    if (elements.inventory) elements.inventory.textContent = `${Math.floor(gameState.inventory)}개`;
    if (elements.staffFatigue) elements.staffFatigue.textContent = `${Math.floor(gameState.staff_fatigue)}점`;
    if (elements.facility) elements.facility.textContent = `${Math.floor(gameState.facility)}점`;
    if (elements.demand) elements.demand.textContent = `${Math.floor(gameState.demand)}점`;
    
    // 경영 정보 업데이트
    if (elements.chickenPrice) elements.chickenPrice.textContent = `${formatNumber(gameState.chicken_price)}원`;
    if (elements.dailyCustomers) elements.dailyCustomers.textContent = `${gameState.daily_customers}명`;
    if (elements.dailyRevenue) elements.dailyRevenue.textContent = `${formatNumber(gameState.daily_revenue)}원`;
    
    // 변화량 표시 (이전 상태와 비교)
    if (previousGameState) {
        if (elements.moneyChange) elements.moneyChange.innerHTML = formatChange(gameState.money, previousGameState.money);
        if (elements.reputationChange) elements.reputationChange.innerHTML = formatChange(gameState.reputation, previousGameState.reputation);
        if (elements.happinessChange) elements.happinessChange.innerHTML = formatChange(gameState.happiness, previousGameState.happiness);
        if (elements.painChange) elements.painChange.innerHTML = formatChange(gameState.pain, previousGameState.pain);
        if (elements.inventoryChange) elements.inventoryChange.innerHTML = formatChange(gameState.inventory, previousGameState.inventory);
        if (elements.staffFatigueChange) elements.staffFatigueChange.innerHTML = formatChange(gameState.staff_fatigue, previousGameState.staff_fatigue);
        if (elements.facilityChange) elements.facilityChange.innerHTML = formatChange(gameState.facility, previousGameState.facility);
        if (elements.demandChange) elements.demandChange.innerHTML = formatChange(gameState.demand, previousGameState.demand);
        
        // 변화가 있는 카드에 펄스 애니메이션
        animateChangedMetrics();
    }
    
    // 이벤트 히스토리 업데이트
    updateEventsHistory();
    
    // 액션 버튼 상태 업데이트
    updateActionButtons();
    
    // 게임 오버 체크
    if (gameState.game_over) {
        showGameOver(gameState.game_over_reason);
    }
    
    // 대화 시스템 트리거 체크
    if (window.DialogueSystem) {
        window.DialogueSystem.checkAutoDialogueTriggers(gameState, previousGameState);
    }
}

/**
 * 변화된 지표에 애니메이션 적용
 */
function animateChangedMetrics() {
    if (!previousGameState) return;
    
    const metrics = [
        { key: 'money', element: document.querySelector('.metric-card.money') },
        { key: 'reputation', element: document.querySelector('.metric-card.reputation') },
        { key: 'happiness', element: document.querySelector('.metric-card.happiness') },
        { key: 'pain', element: document.querySelector('.metric-card.pain') },
        { key: 'inventory', element: document.querySelector('.metric-card.inventory') },
        { key: 'staff_fatigue', element: document.querySelector('.metric-card.staff') },
        { key: 'facility', element: document.querySelector('.metric-card.facility') },
        { key: 'demand', element: document.querySelector('.metric-card.demand') }
    ];
    
    metrics.forEach(({ key, element }) => {
        if (element && gameState[key] !== previousGameState[key]) {
            element.classList.add('pulse');
            setTimeout(() => element.classList.remove('pulse'), 1000);
        }
    });
}

/**
 * 이벤트 히스토리 업데이트
 */
function updateEventsHistory() {
    if (!gameState.events_history || !elements.eventsList) return;
    
    elements.eventsList.innerHTML = '';
    
    gameState.events_history.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        eventItem.innerHTML = `
            <span class="event-icon">📋</span>
            <span class="event-text">${event}</span>
        `;
        elements.eventsList.appendChild(eventItem);
    });
    
    // 스크롤을 최신 이벤트로
    elements.eventsList.scrollTop = elements.eventsList.scrollHeight;
}

/**
 * 액션 버튼 상태 업데이트 (자금 부족 시 비활성화)
 */
function updateActionButtons() {
    if (!gameState) return;
    
    const money = gameState.money;
    
    // 각 액션의 필요 자금과 버튼 매핑
    const actionCosts = {
        'inventoryAction': 50000,
        'staffAction': 30000,
        'promotionAction': 20000,
        'facilityAction': 100000,
        'researchAction': 80000
    };
    
    Object.entries(actionCosts).forEach(([actionId, cost]) => {
        const actionCard = document.getElementById(actionId);
        const button = actionCard?.querySelector('.btn');
        
        if (button) {
            const canAfford = money >= cost;
            button.disabled = !canAfford || isLoading;
            button.classList.toggle('disabled', !canAfford || isLoading);
            
            if (!canAfford) {
                button.title = `자금 부족 (${formatNumber(cost)}원 필요)`;
            } else {
                button.title = '';
            }
        }
    });
    
    // 가격 인하는 최소 가격 체크
    const priceDownButton = document.querySelector('button[onclick*="change: -1000"]');
    if (priceDownButton) {
        const canDecrease = gameState.chicken_price > 5000;
        priceDownButton.disabled = !canDecrease || isLoading;
        priceDownButton.classList.toggle('disabled', !canDecrease || isLoading);
        
        if (!canDecrease) {
            priceDownButton.title = '더 이상 가격을 내릴 수 없습니다';
        }
    }
}

/**
 * 게임 오버 모달 표시
 */
function showGameOver(reason) {
    if (elements.gameOverReason) elements.gameOverReason.textContent = reason || '게임이 종료되었습니다.';
    if (elements.gameOverModal) elements.gameOverModal.classList.add('show');
    
    // 자동 새로고침 중지
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

/**
 * 게임 오버 모달 숨김
 */
function hideGameOver() {
    if (elements.gameOverModal) elements.gameOverModal.classList.remove('show');
}

// ===== 게임 액션 함수 =====

/**
 * 액션 실행 (전역 함수 - HTML onclick에서 호출)
 */
async function executeAction(actionType, parameters = {}) {
    if (isLoading || (gameState && gameState.game_over)) return;
    
    showMessage(`${getActionName(actionType)} 실행 중...`, '⚡');
    
    const result = await executeActionAPI(actionType, parameters);
    
    if (result) {
        if (result.success) {
            showSuccess(result.message);
            updateGameStateUI(result.new_state);
            
            // 턴 진행 시 매일 시작 대화 트리거 (CSV 시스템)
            if (actionType === 'next_turn' && window.csvDialogueSystem) {
                setTimeout(async () => {
                    await window.csvDialogueSystem.triggerDailyStartDialogue();
                }, 2000); // 2초 후 대화 시작
            }
            // 기존 대화 시스템 (폴백용)
            else if (window.DialogueSystem && !window.DialogueSystem.isActive()) {
                triggerActionDialogue(actionType, result.new_state);
            }
        } else {
            showError(result.message);
        }
    }
}

/**
 * 액션 이름 가져오기
 */
function getActionName(actionType) {
    const actionNames = {
        'price_change': '가격 변경',
        'order_inventory': '재료 주문',
        'staff_management': '직원 관리',
        'promotion': '홍보 활동',
        'facility_upgrade': '시설 개선',
        'personal_rest': '개인 휴식',
        'research_development': '연구개발',
        'next_turn': '턴 진행'
    };
    
    return actionNames[actionType] || '알 수 없는 액션';
}

/**
 * 게임 상태 새로고침
 */
async function refreshGameState() {
    const newState = await fetchGameState();
    if (newState) {
        updateGameStateUI(newState);
        showMessage('게임 상태가 새로고침되었습니다.', '🔄');
    }
}

/**
 * 게임 리셋
 */
async function resetGame() {
    if (confirm('정말로 게임을 리셋하시겠습니까? 모든 진행 상황이 사라집니다.')) {
        hideGameOver();
        await resetGameAPI();
        showMessage('새로운 게임을 시작합니다!', '🎮');
        startAutoRefresh();
    }
}

/**
 * 액션별 대화 트리거
 */
function triggerActionDialogue(actionType, newState) {
    // 대화가 이미 활성화되어 있으면 건너뛰기
    if (window.DialogueSystem?.isActive()) return;
    
    // 랜덤하게 대화 실행 (너무 자주 실행되지 않도록)
    const shouldTrigger = Math.random() < 0.3; // 30% 확률
    if (!shouldTrigger) return;
    
    const dialogueMap = {
        'price_change': 'price_increase',
        'order_inventory': 'inventory_order', 
        'staff_management': 'staff_rest',
        'facility_upgrade': 'facility_upgrade'
    };
    
    const dialogueKey = dialogueMap[actionType];
    if (dialogueKey && window.DialogueSystem) {
        setTimeout(() => {
            window.DialogueSystem.startDialogue(dialogueKey);
        }, 1000);
    }
}

// ===== 자동 새로고침 =====

/**
 * 자동 새로고침 시작
 */
function startAutoRefresh() {
    // 기존 인터벌 제거
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // 30초마다 자동 새로고침 (게임 오버가 아닐 때만)
    autoRefreshInterval = setInterval(async () => {
        if (!gameState?.game_over && !isLoading) {
            const newState = await fetchGameState();
            if (newState) {
                updateGameStateUI(newState);
            }
        }
    }, 30000);
}

/**
 * 자동 새로고침 중지
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// ===== 이벤트 리스너 =====

/**
 * 페이지 로드 시 초기화
 */
document.addEventListener('DOMContentLoaded', async function() {
    showMessage('치킨마스터 웹 게임을 시작합니다!', '🍗');
    
    // 초기 게임 상태 로드
    const initialState = await fetchGameState();
    if (initialState) {
        updateGameStateUI(initialState);
        showMessage('게임 데이터를 성공적으로 불러왔습니다.', '✅');
    } else {
        showError('게임 데이터를 불러오는데 실패했습니다. 페이지를 새로고침해주세요.');
        return;
    }
    
    // 자동 새로고침 시작
    startAutoRefresh();
    
    // 키보드 단축키 설정
    setupKeyboardShortcuts();
    
    console.log('🍗 치킨마스터 웹 게임이 성공적으로 초기화되었습니다!');
});

/**
 * 페이지 언로드 시 정리
 */
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});

/**
 * 키보드 단축키 설정
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // 게임 오버 상태에서는 단축키 비활성화
        if (gameState?.game_over || isLoading) return;
        
        // Ctrl/Cmd + 숫자 키로 액션 실행
        if (event.ctrlKey || event.metaKey) {
            switch(event.key) {
                case '1':
                    event.preventDefault();
                    executeAction('price_change', {change: 1000});
                    break;
                case '2':
                    event.preventDefault();
                    executeAction('order_inventory');
                    break;
                case '3':
                    event.preventDefault();
                    executeAction('staff_management');
                    break;
                case '4':
                    event.preventDefault();
                    executeAction('promotion');
                    break;
                case '5':
                    event.preventDefault();
                    executeAction('facility_upgrade');
                    break;
                case '6':
                    event.preventDefault();
                    executeAction('personal_rest');
                    break;
                case '7':
                    event.preventDefault();
                    executeAction('research_development');
                    break;
                case '8':
                    event.preventDefault();
                    executeAction('next_turn');
                    break;
                case 'r':
                    event.preventDefault();
                    refreshGameState();
                    break;
            }
        }
        
        // 스페이스바로 턴 진행
        if (event.code === 'Space' && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            executeAction('next_turn');
        }
    });
}

// ===== 모달 제어 =====

/**
 * 모달 외부 클릭시 닫기
 */
document.addEventListener('DOMContentLoaded', function() {
    if (elements.gameOverModal) {
        elements.gameOverModal.addEventListener('click', function(event) {
            if (event.target === elements.gameOverModal) {
                hideGameOver();
            }
        });
    }
});

// ===== 전역 함수로 노출 (HTML에서 직접 호출용) =====
window.executeAction = executeAction;
window.refreshGameState = refreshGameState;
window.resetGame = resetGame;

// ===== 개발자 도구용 디버그 함수 =====
if (typeof window !== 'undefined') {
    window.ChickenMasterDebug = {
        getGameState: () => gameState,
        getPreviousGameState: () => previousGameState,
        forceRefresh: refreshGameState,
        toggleAutoRefresh: () => {
            if (autoRefreshInterval) {
                stopAutoRefresh();
                console.log('자동 새로고침이 중지되었습니다.');
            } else {
                startAutoRefresh();
                console.log('자동 새로고침이 시작되었습니다.');
            }
        },
        showTestMessage: (text) => showMessage(text, '🧪', 'debug'),
        apiCall: apiCall
    };
    
    console.log('🍗 개발자 도구: window.ChickenMasterDebug 사용 가능');
    console.log('🎮 키보드 단축키:');
    console.log('  Ctrl+1~8: 각종 액션 실행');
    console.log('  Space: 턴 진행');
    console.log('  Ctrl+R: 상태 새로고침');
}
