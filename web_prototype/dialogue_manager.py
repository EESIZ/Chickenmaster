#!/usr/bin/env python3
"""
🍗 치킨마스터 대화 관리자 🍗
CSV 기반 대화 시스템 관리
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Character:
    """캐릭터 정보"""
    character_id: str
    name: str
    avatar_path: str
    voice_description: str
    is_first_person: bool
    default_image: str = ""
    happy_image: str = ""
    sad_image: str = ""
    angry_image: str = ""
    nervous_image: str = ""


@dataclass
class Dialogue:
    """대화 정보"""
    speaker: str
    position: str
    emotion: str
    text: str
    category: str = ""


@dataclass
class ConditionalDialogue:
    """조건부 대화 정보 (매턴 시작용)"""
    condition: str
    money_min: float
    money_max: float
    reputation_min: float
    reputation_max: float
    happiness_min: float
    happiness_max: float
    day_min: int
    day_max: int
    speaker: str
    emotion: str
    text: str
    priority: int


class DialogueManager:
    """CSV 기반 대화 관리자"""
    
    def __init__(self, data_dir: str = "data/dialogues"):
        """대화 매니저 초기화"""
        self.data_dir = Path(data_dir)
        self.characters: Dict[str, Character] = {}
        self.general_dialogues: Dict[str, Dialogue] = {}
        self.daily_start_dialogues: List[ConditionalDialogue] = []
        self.event_dialogues: Dict[str, Dialogue] = {}
        
        # CSV 데이터 로딩
        self._load_all_data()
    
    def _load_all_data(self):
        """모든 CSV 데이터를 로딩"""
        try:
            self._load_characters()
            self._load_general_dialogues() 
            self._load_daily_start_dialogues()
            self._load_event_dialogues()
            print("✅ 모든 대화 데이터가 성공적으로 로딩되었습니다!")
        except Exception as e:
            print(f"⚠️ 대화 데이터 로딩 중 오류: {e}")
            self._load_fallback_data()
    
    def _load_characters(self):
        """캐릭터 정보 로딩"""
        characters_file = self.data_dir / "characters.csv"
        if not characters_file.exists():
            print(f"⚠️ {characters_file} 파일을 찾을 수 없습니다.")
            return
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                character = Character(
                    character_id=row['character_id'],
                    name=row['name'],
                    avatar_path=row['avatar_path'],
                    voice_description=row['voice_description'],
                    is_first_person=row['is_first_person'].lower() == 'true',
                    default_image=row.get('default_image', ''),
                    happy_image=row.get('happy_image', ''),
                    sad_image=row.get('sad_image', ''),
                    angry_image=row.get('angry_image', ''),
                    nervous_image=row.get('nervous_image', '')
                )
                self.characters[character.character_id] = character
    
    def _load_general_dialogues(self):
        """일반 대화 로딩"""
        dialogues_file = self.data_dir / "general_dialogues.csv"
        if not dialogues_file.exists():
            print(f"⚠️ {dialogues_file} 파일을 찾을 수 없습니다.")
            return
        
        with open(dialogues_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dialogue = Dialogue(
                    speaker=row['speaker'],
                    position=row['position'],
                    emotion=row['emotion'],
                    text=row['text'],
                    category=row.get('category', '')
                )
                self.general_dialogues[row['dialogue_id']] = dialogue
    
    def _load_daily_start_dialogues(self):
        """매일 시작 대화 로딩"""
        daily_file = self.data_dir / "daily_start.csv"
        if not daily_file.exists():
            print(f"⚠️ {daily_file} 파일을 찾을 수 없습니다.")
            return
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dialogue = ConditionalDialogue(
                    condition=row['condition'],
                    money_min=float(row['money_min']),
                    money_max=float(row['money_max']),
                    reputation_min=float(row['reputation_min']),
                    reputation_max=float(row['reputation_max']),
                    happiness_min=float(row['happiness_min']),
                    happiness_max=float(row['happiness_max']),
                    day_min=int(row['day_min']),
                    day_max=int(row['day_max']),
                    speaker=row['speaker'],
                    emotion=row['emotion'],
                    text=row['text'],
                    priority=int(row['priority'])
                )
                self.daily_start_dialogues.append(dialogue)
        
        # 우선순위 순으로 정렬
        self.daily_start_dialogues.sort(key=lambda x: x.priority, reverse=True)
    
    def _load_event_dialogues(self):
        """이벤트 대화 로딩"""
        events_file = self.data_dir / "event_dialogues.csv"
        if not events_file.exists():
            print(f"⚠️ {events_file} 파일을 찾을 수 없습니다.")
            return
        
        with open(events_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dialogue = Dialogue(
                    speaker=row['speaker'],
                    position=row['position'],
                    emotion=row['emotion'],
                    text=row['text'],
                    category=row.get('category', '')
                )
                self.event_dialogues[row['event_id']] = dialogue
    
    def _load_fallback_data(self):
        """CSV 로딩 실패시 폴백 데이터"""
        print("📝 폴백 대화 데이터를 사용합니다.")
        
        # 기본 캐릭터
        self.characters = {
            'boss': Character(
                character_id='boss',
                name='나',
                avatar_path='/static/images/icon_chicken_large.png',
                voice_description='나의 생각',
                is_first_person=True
            ),
            'customer': Character(
                character_id='customer',
                name='손님',
                avatar_path='/static/images/customer_character_small.png',
                voice_description='고객',
                is_first_person=False,
                default_image='/static/images/customer_character.png'
            )
        }
        
        # 기본 대화
        self.general_dialogues = {
            'welcome_1': Dialogue(
                speaker='boss',
                position='center',
                emotion='hopeful',
                text='드디어 내 치킨집을 오픈했다! 최고의 치킨집을 만들어보자!',
                category='welcome'
            )
        }
    
    def get_daily_start_dialogue(self, game_state: Dict[str, Any]) -> Optional[Dialogue]:
        """게임 상태에 맞는 매일 시작 대화 반환"""
        money = game_state.get('money', 0)
        reputation = game_state.get('reputation', 0)
        happiness = game_state.get('happiness', 50)
        day = game_state.get('day', 1)
        
        for conditional_dialogue in self.daily_start_dialogues:
            if (conditional_dialogue.money_min <= money <= conditional_dialogue.money_max and
                conditional_dialogue.reputation_min <= reputation <= conditional_dialogue.reputation_max and
                conditional_dialogue.happiness_min <= happiness <= conditional_dialogue.happiness_max and
                conditional_dialogue.day_min <= day <= conditional_dialogue.day_max):
                
                return Dialogue(
                    speaker=conditional_dialogue.speaker,
                    position='center',
                    emotion=conditional_dialogue.emotion,
                    text=conditional_dialogue.text,
                    category='daily_start'
                )
        
        # 조건에 맞는 대화가 없으면 기본 대화
        return self.general_dialogues.get('welcome_1')
    
    def get_dialogue(self, dialogue_id: str) -> Optional[Dialogue]:
        """ID로 일반 대화 반환"""
        return self.general_dialogues.get(dialogue_id)
    
    def get_event_dialogue(self, event_id: str) -> Optional[Dialogue]:
        """이벤트 대화 반환"""
        return self.event_dialogues.get(event_id)
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """캐릭터 정보 반환"""
        return self.characters.get(character_id)
    
    def get_dialogue_by_category(self, category: str) -> List[Dialogue]:
        """카테고리별 대화 목록 반환"""
        return [dialogue for dialogue in self.general_dialogues.values() 
                if dialogue.category == category]
    
    def to_javascript_format(self) -> Dict[str, Any]:
        """JavaScript에서 사용할 수 있는 형태로 변환"""
        # 캐릭터 데이터베이스
        character_db = {}
        for char_id, char in self.characters.items():
            images = {}
            if char.default_image:
                images['default'] = char.default_image
            if char.happy_image:
                images['happy'] = char.happy_image
            if char.sad_image:
                images['sad'] = char.sad_image
            if char.angry_image:
                images['angry'] = char.angry_image
            if char.nervous_image:
                images['nervous'] = char.nervous_image
            
            character_db[char_id] = {
                'name': char.name,
                'avatar': char.avatar_path,
                'images': images,
                'voice': char.voice_description,
                'isFirstPerson': char.is_first_person
            }
        
        # 대화 스크립트
        dialogue_scripts = {}
        for dialogue_id, dialogue in self.general_dialogues.items():
            if dialogue.category not in dialogue_scripts:
                dialogue_scripts[dialogue.category] = []
            
            dialogue_scripts[dialogue.category].append({
                'speaker': dialogue.speaker,
                'position': dialogue.position,
                'emotion': dialogue.emotion,
                'text': dialogue.text
            })
        
        return {
            'CHARACTER_DATABASE': character_db,
            'DIALOGUE_SCRIPTS': dialogue_scripts
        }


# 전역 대화 매니저 인스턴스
dialogue_manager = DialogueManager() 