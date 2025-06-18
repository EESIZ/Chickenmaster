"""
치킨마스터 웹 게임용 임시 placeholder 이미지 생성기
외부에서 실제 이미지를 만들기 전에 레이아웃 테스트용으로 사용
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# 이미지 저장 경로
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(exist_ok=True)

# 기본 색상 팔레트 (치킨마스터 테마)
COLORS = {
    "chicken_orange": "#ff6b35",
    "warm_yellow": "#ffd700", 
    "bg_cream": "#fff8e1",
    "text_brown": "#2c1810",
    "success_green": "#27ae60",
    "danger_red": "#e74c3c",
    "purple": "#9b59b6",
    "blue": "#3498db"
}

def create_simple_icon(size: tuple, color: str, text: str, filename: str):
    """간단한 아이콘 이미지 생성"""
    img = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(img)
    
    # 텍스트 크기 계산해서 중앙에 배치
    try:
        font = ImageFont.truetype("arial.ttf", size[0]//3)
    except:
        font = ImageFont.load_default()
    
    # 텍스트를 중앙에 배치
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill="white", font=font)
    
    img.save(IMAGES_DIR / filename)
    print(f"✅ Created: {filename}")

def create_background_image(size: tuple, filename: str):
    """치킨집 배경 이미지 생성"""
    img = Image.new('RGB', size, COLORS["bg_cream"])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션 효과 (간단하게)
    for i in range(size[1]):
        alpha = i / size[1]
        r = int(255 * (1 - alpha * 0.1))
        g = int(248 * (1 - alpha * 0.1))
        b = int(225 * (1 - alpha * 0.1))
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))
    
    # 치킨집 느낌의 장식 요소들 추가
    draw.rectangle([50, 50, size[0]-50, size[1]-50], outline=COLORS["chicken_orange"], width=5)
    
    # 중앙에 "치킨집" 텍스트
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    text = "🍗 우리 치킨집 🍗"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=COLORS["chicken_orange"], font=font)
    
    img.save(IMAGES_DIR / filename)
    print(f"✅ Created: {filename}")

def create_character_image(size: tuple, filename: str, character_type="boss", emotion="default"):
    """캐릭터 이미지 생성 (다양한 표정 지원)"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # 투명 배경
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size[0] // 2, size[1] // 2
    
    if character_type == "boss":
        # 사장님 캐릭터
        # 머리
        head_color = COLORS["warm_yellow"]
        if emotion == "angry":
            head_color = "#ffaa00"
        elif emotion == "sad":
            head_color = "#e6d700"
            
        draw.ellipse([center_x-40, center_y-60, center_x+40, center_y+20], 
                    fill=head_color, outline=COLORS["text_brown"], width=2)
        
        # 표정 그리기
        if emotion == "happy":
            # 웃는 눈
            draw.arc([center_x-30, center_y-40, center_x-10, center_y-30], 0, 180, fill=COLORS["text_brown"], width=3)
            draw.arc([center_x+10, center_y-40, center_x+30, center_y-30], 0, 180, fill=COLORS["text_brown"], width=3)
            # 웃는 입
            draw.arc([center_x-15, center_y-15, center_x+15, center_y-5], 0, 180, fill=COLORS["text_brown"], width=3)
        elif emotion == "sad":
            # 슬픈 눈
            draw.ellipse([center_x-25, center_y-35, center_x-20, center_y-30], fill=COLORS["text_brown"])
            draw.ellipse([center_x+20, center_y-35, center_x+25, center_y-30], fill=COLORS["text_brown"])
            # 슬픈 입
            draw.arc([center_x-10, center_y-5, center_x+10, center_y+5], 180, 360, fill=COLORS["text_brown"], width=3)
        elif emotion == "angry":
            # 화난 눈썹
            draw.line([center_x-30, center_y-45, center_x-15, center_y-40], fill=COLORS["danger_red"], width=4)
            draw.line([center_x+15, center_y-40, center_x+30, center_y-45], fill=COLORS["danger_red"], width=4)
            # 화난 눈
            draw.ellipse([center_x-25, center_y-35, center_x-20, center_y-30], fill=COLORS["danger_red"])
            draw.ellipse([center_x+20, center_y-35, center_x+25, center_y-30], fill=COLORS["danger_red"])
        else:  # default
            # 평범한 눈
            draw.ellipse([center_x-25, center_y-35, center_x-20, center_y-30], fill=COLORS["text_brown"])
            draw.ellipse([center_x+20, center_y-35, center_x+25, center_y-30], fill=COLORS["text_brown"])
        
        # 몸
        draw.rectangle([center_x-30, center_y+20, center_x+30, center_y+80], 
                      fill=COLORS["chicken_orange"], outline=COLORS["text_brown"], width=2)
        
        # 앞치마
        draw.rectangle([center_x-25, center_y+30, center_x+25, center_y+75], 
                      fill="white", outline=COLORS["text_brown"], width=1)
                      
        label = "사장님"
        
    elif character_type == "customer":
        # 손님 캐릭터
        # 머리 (다른 색상)
        draw.ellipse([center_x-35, center_y-55, center_x+35, center_y+15], 
                    fill=COLORS["purple"], outline=COLORS["text_brown"], width=2)
        
        # 기본 눈
        draw.ellipse([center_x-20, center_y-30, center_x-15, center_y-25], fill=COLORS["text_brown"])
        draw.ellipse([center_x+15, center_y-30, center_x+20, center_y-25], fill=COLORS["text_brown"])
        
        # 몸 (다른 색상)
        draw.rectangle([center_x-25, center_y+15, center_x+25, center_y+75], 
                      fill=COLORS["blue"], outline=COLORS["text_brown"], width=2)
                      
        label = "손님"
    
    # 텍스트 추가
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    x = (size[0] - text_width) // 2
    draw.text((x, center_y+85), label, fill=COLORS["text_brown"], font=font)
    
    img.save(IMAGES_DIR / filename)
    print(f"✅ Created: {filename}")

def main():
    """모든 placeholder 이미지 생성"""
    print("🎨 치킨마스터 placeholder 이미지 생성 시작!")
    
    # UI 아이콘들 (32x32)
    icons = [
        ("money", COLORS["success_green"], "$"),
        ("chicken", COLORS["chicken_orange"], "🍗"),
        ("reputation", COLORS["warm_yellow"], "★"),
        ("happiness", COLORS["success_green"], "😊"),
        ("pain", COLORS["danger_red"], "😰"),
        ("inventory", COLORS["chicken_orange"], "📦"),
        ("fatigue", COLORS["purple"], "😴"),  
        ("facility", COLORS["blue"], "🏪"),
        ("demand", COLORS["success_green"], "📈"),
    ]
    
    for name, color, symbol in icons:
        create_simple_icon((32, 32), color, symbol, f"icon_{name}.png")
    
    # 더 큰 아이콘들 (64x64)
    for name, color, symbol in icons:
        create_simple_icon((64, 64), color, symbol, f"icon_{name}_large.png")
    
    # 배경 이미지들
    create_background_image((800, 600), "chicken_shop_bg.png")
    create_background_image((400, 300), "chicken_shop_bg_small.png")
    
    # 사장님 캐릭터 - 다양한 표정
    create_character_image((200, 200), "boss_character.png", "boss", "default")
    create_character_image((200, 200), "boss_character_happy.png", "boss", "happy")
    create_character_image((200, 200), "boss_character_sad.png", "boss", "sad")  
    create_character_image((200, 200), "boss_character_angry.png", "boss", "angry")
    
    # 사장님 작은 버전
    create_character_image((150, 150), "boss_character_small.png", "boss", "default")
    create_character_image((150, 150), "boss_character_small_happy.png", "boss", "happy")
    create_character_image((150, 150), "boss_character_small_sad.png", "boss", "sad")
    create_character_image((150, 150), "boss_character_small_angry.png", "boss", "angry")
    
    # 손님 캐릭터
    create_character_image((200, 200), "customer_character.png", "customer", "default")
    create_character_image((150, 150), "customer_character_small.png", "customer", "default")
    
    # 버튼 배경들
    create_simple_icon((200, 50), COLORS["chicken_orange"], "액션", "button_bg.png")
    create_simple_icon((200, 50), COLORS["success_green"], "성공", "button_success.png")
    create_simple_icon((200, 50), COLORS["danger_red"], "위험", "button_danger.png")
    
    print("\n🎉 모든 placeholder 이미지 생성 완료!")
    print(f"📁 저장 위치: {IMAGES_DIR.absolute()}")
    print("\n📋 생성된 파일들:")
    for file in sorted(IMAGES_DIR.glob("*.png")):
        print(f"   - {file.name}")

if __name__ == "__main__":
    main() 