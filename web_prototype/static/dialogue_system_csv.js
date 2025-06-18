/**
 * 🍗 치킨마스터 CSV 기반 대화 시스템 JavaScript 🍗
 * 
 * 서버의 CSV 데이터를 활용한 동적 대화 시스템
 */

// ===== 대화 시스템 전역 변수 =====
let currentDialogue = null;
let dialogueQueue = [];
let isDialogueActive = false;
let currentCharacterStates = {
    left: null,
    center: null,
    right: null
};

// CSV에서 로딩된 데이터
let CHARACTER_DATABASE = {};
let DIALOGUE_SCRIPTS = {};

// ===== 대화 시스템 설정 =====
const DIALOGUE_CONFIG = {
    typewriterSpeed: 50,
    autoAdvanceDelay: 3000,
    characterTransitionSpeed: 500,
};

// ===== DOM 요소 캐싱 =====
const dialogueElements = {
    dialogueSystem: document.getElementById('dialogueSystem'),
    dialogueBox: document.getElementById('dialogueBox'),
    speakerAvatar: document.getElementById('speakerAvatar'),
    speakerName: document.getElementById('speakerName'),
    dialogueText: document.getElementById('dialogueText'),
    continueBtn: document.getElementById('continueBtn'),
    skipBtn: document.getElementById('skipBtn'),
    
    backgroundImage: document.getElementById('backgroundImage'),
    characterLeft: document.getElementById('characterLeftImg'),
    characterCenter: document.getElementById('characterCenterImg'),
    characterRight: document.getElementById('characterRightImg'),
    
    locationName: document.getElementById('locationName'),
    timeInfo: document.getElementById('timeInfo')
};

// ===== 초기화 함수 =====

/**
 * CSV 대화 시스템 초기화
 */
async function initializeDialogueSystem() {
    try {
        console.log('🔄 CSV 대화 시스템 초기화 중...');
        
        // 서버에서 캐릭터 데이터베이스 로딩
        const response = await fetch('/api/dialogue/character-database');
        const result = await response.json();
        
        if (result.success) {
            CHARACTER_DATABASE = result.data.CHARACTER_DATABASE;
            DIALOGUE_SCRIPTS = result.data.DIALOGUE_SCRIPTS;
            console.log('✅ CSV 대화 데이터 로딩 완료');
            console.log('📊 로딩된 캐릭터:', Object.keys(CHARACTER_DATABASE));
            console.log('📊 로딩된 대화 카테고리:', Object.keys(DIALOGUE_SCRIPTS));
        } else {
            console.error('❌ 대화 데이터 로딩 실패:', result.error);
            loadFallbackData();
        }
        
    } catch (error) {
        console.error('❌ 대화 시스템 초기화 오류:', error);
        loadFallbackData();
    }
}

/**
 * 폴백 데이터 로딩 (서버 연결 실패시)
 */
function loadFallbackData() {
    console.log('📝 폴백 대화 데이터 사용');
    
    CHARACTER_DATABASE = {
        boss: {
            name: "나",
            avatar: "/static/images/icon_chicken_large.png",
            images: {},
            voice: "나의 생각",
            isFirstPerson: true
        },
        customer: {
            name: "손님",
            avatar: "/static/images/customer_character_small.png",
            images: {
                default: "/static/images/customer_character.png"
            },
            voice: "고객",
            isFirstPerson: false
        }
    };
    
    DIALOGUE_SCRIPTS = {
        welcome: [
            {
                speaker: "boss",
                position: "center",
                emotion: "hopeful",
                text: "드디어 내 치킨집을 오픈했다! 최고의 치킨집을 만들어보자!"
            }
        ]
    };
}

// ===== 대화 시스템 핵심 함수 =====

/**
 * 매일 시작 대화 가져오기 (서버에서 동적으로)
 */
async function getDailyStartDialogue() {
    try {
        const response = await fetch('/api/dialogue/daily-start');
        const result = await response.json();
        
        if (result.success) {
            return [result.dialogue]; // 배열 형태로 반환
        } else {
            console.error('매일 시작 대화 가져오기 실패:', result.message);
            return null;
        }
    } catch (error) {
        console.error('매일 시작 대화 API 오류:', error);
        return null;
    }
}

/**
 * 이벤트 대화 가져오기
 */
async function getEventDialogue(eventId) {
    try {
        const response = await fetch(`/api/dialogue/event/${eventId}`);
        const result = await response.json();
        
        if (result.success) {
            return [result.dialogue];
        } else {
            console.error(`이벤트 대화 '${eventId}' 가져오기 실패:`, result.message);
            return null;
        }
    } catch (error) {
        console.error('이벤트 대화 API 오류:', error);
        return null;
    }
}

/**
 * 대화 시작 (동적 로딩 버전)
 */
async function startDialogue(scriptKeyOrDialogues) {
    let script = null;
    
    // 문자열이면 서버에서 가져오기
    if (typeof scriptKeyOrDialogues === 'string') {
        if (scriptKeyOrDialogues === 'daily_start') {
            script = await getDailyStartDialogue();
        } else if (scriptKeyOrDialogues.startsWith('event_')) {
            const eventId = scriptKeyOrDialogues.replace('event_', '');
            script = await getEventDialogue(eventId);
        } else {
            // 기존 스크립트에서 찾기
            script = DIALOGUE_SCRIPTS[scriptKeyOrDialogues];
        }
    } else {
        // 배열이면 직접 사용
        script = scriptKeyOrDialogues;
    }
    
    if (!script) {
        console.error('대화를 찾을 수 없습니다:', scriptKeyOrDialogues);
        return;
    }
    
    dialogueQueue = [...script];
    isDialogueActive = true;
    showDialogueSystem();
    nextDialogue();
}

/**
 * 게임 상태 기반 자동 대화 트리거
 */
async function triggerDailyStartDialogue() {
    console.log('🌅 매일 시작 대화 트리거');
    await startDialogue('daily_start');
}

/**
 * 대화창 시스템 표시
 */
function showDialogueSystem() {
    if (dialogueElements.dialogueSystem) {
        dialogueElements.dialogueSystem.style.display = 'block';
        dialogueElements.dialogueBox.classList.remove('hidden');
        dialogueElements.dialogueBox.classList.add('appear');
    }
}

/**
 * 대화창 시스템 숨김
 */
function hideDialogueSystem() {  
    if (dialogueElements.dialogueBox) {
        dialogueElements.dialogueBox.classList.add('hidden');
        
        setTimeout(() => {
            hideAllNPCCharacters();
        }, 500);
        
        setTimeout(() => {
            if (dialogueElements.dialogueSystem) {
                dialogueElements.dialogueSystem.style.display = 'none';
            }
            isDialogueActive = false;
        }, 300);
    }
}

/**
 * 모든 NPC 캐릭터 숨기기
 */
function hideAllNPCCharacters() {
    const positions = ['left', 'center', 'right'];
    
    positions.forEach(position => {
        if (currentCharacterStates[position]) {
            const characterId = currentCharacterStates[position].characterId;
            const character = CHARACTER_DATABASE[characterId];
            
            if (!character?.isFirstPerson) {
                const element = document.getElementById(`character${position.charAt(0).toUpperCase() + position.slice(1)}`);
                if (element) {
                    element.style.opacity = '0';
                    setTimeout(() => {
                        element.style.display = 'none';
                        element.src = '';
                    }, 500);
                }
                currentCharacterStates[position] = null;
            }
        }
    });
}

/**
 * 다음 대화로 진행
 */
function nextDialogue() {
    if (dialogueQueue.length === 0) {
        hideDialogueSystem();
        return;
    }
    
    currentDialogue = dialogueQueue.shift();
    displayDialogue(currentDialogue);
}

/**
 * 대화 표시
 */
function displayDialogue(dialogue) {
    if (!dialogue) return;
    
    setCharacter(dialogue.speaker, dialogue.position, dialogue.emotion);
    updateSpeakerInfo(dialogue.speaker);
    animateText(dialogue.text);
    highlightActiveCharacter(dialogue.position);
}

/**
 * 캐릭터 설정
 */
function setCharacter(characterId, position, emotion = 'default') {
    const character = CHARACTER_DATABASE[characterId];
    if (!character) {
        console.error('캐릭터를 찾을 수 없습니다:', characterId);
        return;
    }
    
    if (character.isFirstPerson) {
        return; // 1인칭 캐릭터는 표시하지 않음
    }
    
    const characterElement = dialogueElements[`character${position.charAt(0).toUpperCase() + position.slice(1)}`];
    if (!characterElement) return;
    
    const imageSrc = character.images[emotion] || character.images.default;
    characterElement.src = imageSrc;
    characterElement.style.display = 'block';
    
    characterElement.style.opacity = '0';
    setTimeout(() => {
        characterElement.style.opacity = '1';
    }, 100);
    
    currentCharacterStates[position] = {
        characterId,
        emotion
    };
}

/**
 * 화자 정보 업데이트
 */
function updateSpeakerInfo(characterId) {
    const character = CHARACTER_DATABASE[characterId];
    if (!character) return;
    
    const avatarImg = dialogueElements.speakerAvatar?.querySelector('img');
    if (avatarImg) {
        avatarImg.src = character.avatar;
    }
    
    if (dialogueElements.speakerName) {
        dialogueElements.speakerName.textContent = character.name;
    }
}

/**
 * 텍스트 애니메이션
 */
function animateText(text) {
    if (!dialogueElements.dialogueText) return;
    
    dialogueElements.dialogueText.textContent = '';
    dialogueElements.dialogueText.classList.add('typing');
    
    let index = 0;
    const typeInterval = setInterval(() => {
        if (index < text.length) {
            dialogueElements.dialogueText.textContent += text[index];
            index++;
        } else {
            clearInterval(typeInterval);
            dialogueElements.dialogueText.classList.remove('typing');
        }
    }, DIALOGUE_CONFIG.typewriterSpeed);
}

/**
 * 활성 캐릭터 강조
 */
function highlightActiveCharacter(activePosition) {
    const positions = ['left', 'center', 'right'];
    
    positions.forEach(position => {
        const element = document.getElementById(`character${position.charAt(0).toUpperCase() + position.slice(1)}`);
        if (element && element.style.display !== 'none') {
            if (position === activePosition) {
                element.classList.add('active');
                element.classList.remove('inactive');
            } else if (currentCharacterStates[position]) {
                element.classList.add('inactive');
                element.classList.remove('active');
            }
        }
    });
    
    if (currentDialogue?.speaker) {
        const speakerCharacter = CHARACTER_DATABASE[currentDialogue.speaker];
        if (speakerCharacter?.isFirstPerson) {
            positions.forEach(position => {
                const element = document.getElementById(`character${position.charAt(0).toUpperCase() + position.slice(1)}`);
                if (element && element.style.display !== 'none') {
                    element.classList.add('inactive');
                    element.classList.remove('active');
                }
            });
        }
    }
}

// ===== 대화 제어 함수 =====

function continueDialogue() {
    if (!isDialogueActive) return;
    nextDialogue();
}

function skipDialogue() {
    if (!isDialogueActive) return;
    dialogueQueue = [];
    hideDialogueSystem();
}

// ===== 자동 초기화 =====

// 페이지 로드시 자동 초기화
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🍗 CSV 대화 시스템 로딩 시작...');
    await initializeDialogueSystem();
    
    // 게임 시작시 대화 트리거 (1초 후)
    setTimeout(async () => {
        await triggerDailyStartDialogue();
    }, 1000);
});

// 전역 함수로 내보내기
window.csvDialogueSystem = {
    startDialogue,
    triggerDailyStartDialogue,
    initializeDialogueSystem,
    continueDialogue,
    skipDialogue
}; 