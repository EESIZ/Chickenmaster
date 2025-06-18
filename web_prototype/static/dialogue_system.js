/**
 * 🍗 치킨마스터 대화 시스템 JavaScript 🍗
 * 
 * 비주얼 노벨 스타일의 대화 및 캐릭터 시스템
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

// ===== 대화 시스템 설정 =====
const DIALOGUE_CONFIG = {
    typewriterSpeed: 50, // 타이핑 효과 속도 (ms)
    autoAdvanceDelay: 3000, // 자동 진행 딜레이 (ms)
    characterTransitionSpeed: 500, // 캐릭터 전환 속도 (ms)
};

// ===== 캐릭터 정보 데이터베이스 =====
const CHARACTER_DATABASE = {
    boss: {
        name: "나",
        avatar: "/static/images/icon_chicken_large.png", // 1인칭이므로 치킨 아이콘 사용
        images: {
            // 1인칭 주인공은 이미지가 표시되지 않음
        },
        voice: "나의 생각",
        isFirstPerson: true // 1인칭 캐릭터 플래그
    },
    customer: {
        name: "손님",
        avatar: "/static/images/customer_character_small.png",
        images: {
            default: "/static/images/customer_character.png",
            happy: "/static/images/customer_character.png",
            sad: "/static/images/customer_character.png"
        },
        voice: "고객"
    },
    assistant: {
        name: "도우미",
        avatar: "/static/images/boss_character_small.png",
        images: {
            default: "/static/images/boss_character.png",
            happy: "/static/images/boss_character_happy.png"
        },
        voice: "게임 도우미"
    }
};

// ===== 대화 스크립트 데이터베이스 =====
const DIALOGUE_SCRIPTS = {
    welcome: [
        {
            speaker: "boss",
            position: "center",
            emotion: "happy",
            text: "드디어 내 치킨집을 오픈했다! 최고의 치킨집을 만들어보자!"
        },
        {
            speaker: "boss", 
            position: "center",
            emotion: "default",
            text: "오른쪽 패널에서 경영 액션을 선택하고, 왼쪽에서 매장 상태를 확인할 수 있다."
        }
    ],
    
    first_customer: [
        {
            speaker: "customer",
            position: "center",
            emotion: "happy",
            text: "안녕하세요! 새로 오픈한 치킨집이네요. 치킨 하나 주세요!"
        },
        {
            speaker: "boss",
            position: "center",
            emotion: "happy",
            text: "첫 손님이다! 잘 해보자. 맛있는 치킨 만들어드릴게요!"
        },
        {
            speaker: "boss",
            position: "center",
            emotion: "default",
            text: "자, 이제 본격적으로 시작해보자! 성공적인 치킨집 사장이 되어보겠어!"
        }
    ],
    
    daily_start: [
        {
            speaker: "boss",
            position: "center",
            emotion: "default", 
            text: "새로운 하루가 시작됐다. 오늘은 어떤 경영 전략을 써볼까?"
        }
    ],
    
    low_money: [
        {
            speaker: "boss",
            position: "center",
            emotion: "sad",
            text: "자금이 부족해지고 있다... 가격 인상이나 홍보를 고려해봐야겠어."
        }
    ],
    
    high_reputation: [
        {
            speaker: "boss",
            position: "center", 
            emotion: "happy",
            text: "와! 우리 매장 평판이 정말 좋아졌네! 손님들이 많이 찾아오고 있어!"
        }
    ],
    
    game_over: [
        {
            speaker: "boss",
            position: "center",
            emotion: "sad", 
            text: "아쉽게도 사업이 어려워졌다... 하지만 포기하지 말자! 다시 도전해보자!"
        }
    ],
    
    customer_visit: [
        {
            speaker: "customer",
            position: "center",
            emotion: "happy",
            text: "안녕하세요! 치킨 주문하러 왔어요!"
        },
        {
            speaker: "boss",
            position: "center", 
            emotion: "happy",
            text: "손님이 왔다! 맛있는 치킨을 준비해주자."
        }
    ],
    
    price_increase: [
        {
            speaker: "boss",
            position: "center",
            emotion: "default",
            text: "치킨 가격을 인상했다. 고객 반응을 지켜봐야겠어."
        }
    ],
    
    inventory_order: [
        {
            speaker: "boss", 
            position: "center",
            emotion: "happy",
            text: "재료를 주문했다! 이제 더 많은 치킨을 만들 수 있겠어."
        }
    ],
    
    staff_rest: [
        {
            speaker: "boss",
            position: "center",
            emotion: "happy", 
            text: "직원들에게 휴식을 줬다. 더 열심히 일할 수 있을 거야!"
        }
    ],
    
    high_pain: [
        {
            speaker: "boss",
            position: "center", 
            emotion: "angry",
            text: "스트레스가 너무 심하다... 좀 쉬어야겠어."
        }
    ],
    
    facility_upgrade: [
        {
            speaker: "boss",
            position: "center",
            emotion: "happy",
            text: "시설을 업그레이드했다! 더 좋은 환경에서 치킨을 만들 수 있겠어."
        }
    ],
    
    busy_day: [
        {
            speaker: "customer",
            position: "left",
            emotion: "happy",
            text: "저기요! 치킨 하나 주세요!"
        },
        {
            speaker: "boss",
            position: "center",
            emotion: "default",
            text: "바쁜 하루네. 하지만 이런 게 좋지!"
        }
    ],
    
    lonely_day: [
        {
            speaker: "boss",
            position: "center",
            emotion: "sad",
            text: "오늘은 손님이 별로 없네... 뭔가 대책이 필요할까?"
        }
    ],
    
    success_moment: [
        {
            speaker: "boss",
            position: "center",
            emotion: "happy",
            text: "와! 치킨집이 점점 잘 되가고 있어! 이 기세로 계속 가보자!"
        }
    ]
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

// ===== 대화 시스템 핵심 함수 =====

/**
 * 대화 시작
 */
function startDialogue(scriptKey) {
    const script = DIALOGUE_SCRIPTS[scriptKey];
    if (!script) {
        console.error('대화 스크립트를 찾을 수 없습니다:', scriptKey);
        return;
    }
    
    dialogueQueue = [...script];
    isDialogueActive = true;
    showDialogueSystem();
    nextDialogue();
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
        
        // NPC 캐릭터들 자동으로 사라지게 하기
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
 * 모든 NPC 캐릭터 숨기기 (1인칭 캐릭터 제외)
 */
function hideAllNPCCharacters() {
    const positions = ['left', 'center', 'right'];
    
    positions.forEach(position => {
        if (currentCharacterStates[position]) {
            const characterId = currentCharacterStates[position].characterId;
            const character = CHARACTER_DATABASE[characterId];
            
            // 1인칭 캐릭터가 아닌 경우에만 숨기기
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
    
    // 캐릭터 설정
    setCharacter(dialogue.speaker, dialogue.position, dialogue.emotion);
    
    // 화자 정보 업데이트
    updateSpeakerInfo(dialogue.speaker);
    
    // 텍스트 애니메이션
    animateText(dialogue.text);
    
    // 캐릭터 강조 효과
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
    
    // 1인칭 캐릭터는 화면에 표시하지 않음
    if (character.isFirstPerson) {
        return;
    }
    
    const characterElement = dialogueElements[`character${position.charAt(0).toUpperCase() + position.slice(1)}`];
    if (!characterElement) return;
    
    // 캐릭터 이미지 설정
    const imageSrc = character.images[emotion] || character.images.default;
    characterElement.src = imageSrc;
    characterElement.style.display = 'block';
    
    // 전환 애니메이션
    characterElement.style.opacity = '0';
    setTimeout(() => {
        characterElement.style.opacity = '1';
    }, 100);
    
    // 현재 캐릭터 상태 저장
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
    
    // 아바타 이미지
    const avatarImg = dialogueElements.speakerAvatar?.querySelector('img');
    if (avatarImg) {
        avatarImg.src = character.avatar;
    }
    
    // 화자 이름
    if (dialogueElements.speakerName) {
        dialogueElements.speakerName.textContent = character.name;
    }
}

/**
 * 텍스트 애니메이션 (타이핑 효과)
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
    
    // 1인칭 캐릭터가 말할 때는 모든 다른 캐릭터를 비활성화
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

/**
 * 배경 변경
 */
function changeBackground(backgroundSrc) {
    if (dialogueElements.backgroundImage) {
        dialogueElements.backgroundImage.style.opacity = '0';
        setTimeout(() => {
            dialogueElements.backgroundImage.src = backgroundSrc;
            dialogueElements.backgroundImage.style.opacity = '1';
        }, 400);
    }
}

/**
 * 위치 정보 업데이트
 */
function updateLocationInfo(locationName, timeInfo) {
    if (dialogueElements.locationName) {
        dialogueElements.locationName.textContent = locationName;
    }
    if (dialogueElements.timeInfo) {
        dialogueElements.timeInfo.textContent = timeInfo;
    }
}

// ===== 대화 제어 함수 (HTML에서 호출) =====

/**
 * 대화 계속 진행
 */
function continueDialogue() {
    if (!isDialogueActive) return;
    nextDialogue();
}

/**
 * 대화 건너뛰기
 */
function skipDialogue() {
    if (!isDialogueActive) return;
    hideDialogueSystem();
}

// ===== 게임 이벤트와 연동 =====

/**
 * 게임 상태에 따른 자동 대화 트리거
 */
function checkAutoDialogueTriggers(gameState, previousState) {
    if (!gameState) return;
    
    // 게임 시작 시
    if (!previousState && gameState.day === 1) {
        setTimeout(() => {
            startDialogue('welcome');
            // 웰컴 대화 후 첫 손님 등장
            setTimeout(() => {
                if (!isDialogueActive) {
                    startDialogue('first_customer');
                }
            }, 8000); // 웰컴 대화가 끝날 시간을 고려
        }, 1000);
        return;
    }
    
    // 게임 오버 시
    if (gameState.game_over && !previousState?.game_over) {
        setTimeout(() => startDialogue('game_over'), 500);
        return;
    }
    
    // 자금 부족 경고
    if (gameState.money < 30000 && !isDialogueActive) {
        if (!previousState || previousState.money >= 30000) {
            setTimeout(() => startDialogue('low_money'), 2000);
        }
    }
    
    // 평판 상승 축하
    if (gameState.reputation >= 80 && !isDialogueActive) {
        if (!previousState || previousState.reputation < 80) {
            setTimeout(() => startDialogue('high_reputation'), 1500);
        }
    }
    
    // 새 하루 시작
    if (gameState.day > (previousState?.day || 0) && !gameState.game_over) {
        setTimeout(() => startDialogue('daily_start'), 1000);
    }
    
    // 높은 고통 상태 경고
    if (gameState.pain >= 80 && !isDialogueActive) {
        if (!previousState || previousState.pain < 80) {
            setTimeout(() => startDialogue('high_pain'), 1500);
        }
    }
    
    // 손님이 많이 올 때 (바쁜 날)
    if (gameState.daily_customers > 25 && !isDialogueActive) {
        if (!previousState || previousState.daily_customers <= 25) {
            setTimeout(() => startDialogue('busy_day'), 2000);
        }
    }
    
    // 손님이 적을 때 (한가한 날)
    if (gameState.daily_customers < 5 && gameState.day > 3 && !isDialogueActive) {
        if (!previousState || previousState.daily_customers >= 5) {
            setTimeout(() => startDialogue('lonely_day'), 2500);
        }
    }
    
    // 성공 순간 (높은 매출 + 높은 평판)
    if (gameState.daily_revenue > 200000 && gameState.reputation > 70 && !isDialogueActive) {
        if (!previousState || previousState.daily_revenue <= 200000) {
            setTimeout(() => startDialogue('success_moment'), 3000);
        }
    }
}

/**
 * 커스텀 대화 추가
 */
function addCustomDialogue(scriptKey, dialogueScript) {
    DIALOGUE_SCRIPTS[scriptKey] = dialogueScript;
}

/**
 * 캐릭터 추가
 */
function addCharacter(characterId, characterData) {
    CHARACTER_DATABASE[characterId] = characterData;
}

// ===== 키보드 단축키 =====
document.addEventListener('keydown', (event) => {
    if (!isDialogueActive) return;
    
    switch(event.key) {
        case 'Enter':
        case ' ':
            event.preventDefault();
            continueDialogue();
            break;
        case 'Escape':
            event.preventDefault();
            skipDialogue();
            break;
    }
});

// ===== 초기화 =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎭 대화 시스템이 로드되었습니다!');
    
    // 대화창 초기 상태 (숨김)
    if (dialogueElements.dialogueSystem) {
        dialogueElements.dialogueSystem.style.display = 'none';
    }
});

// ===== 전역 함수 export (다른 스크립트에서 사용) =====
window.DialogueSystem = {
    startDialogue,
    addCustomDialogue,
    addCharacter,
    changeBackground,
    updateLocationInfo,
    checkAutoDialogueTriggers,
    isActive: () => isDialogueActive
}; 