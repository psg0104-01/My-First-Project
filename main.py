import json
import random
import os

# 자원 목록 정의 (상자류 포함)
item_mineral = ["돌", "주석", "철", "은", "금", "티타늄", "에메랄드", "루비", "사파이어", "다이아몬드", "방사능", "토륨", "라듐", "방사능상자"]

# 확률 정의 (자원 개수와 맞춰야 함)
item_prob = [3700, 1700, 1300, 1000, 800, 500, 400, 100, 200, 50, 250]
if len(item_mineral) != len(item_prob):
    item_prob = [1] * len(item_mineral)

# 제작 레시피 정의
recipes = {
    ''' 양식 : "아이템이름": {"재료1": 개수1, "재료2": 개수2, ...} '''
    "방사능상자": {"방사능": 3}
}

# 상자 보상 정의
box_rewards = {

    "방사능상자": {
        "아이템": ["토륨", "라듐"],
        "확률": [70, 30],
        "개수": {  # {개수: 확률} 형식
            2: 40,  # 2개가 나올 확률 40%
            3: 30,  # 3개가 나올 확률 30%
            4: 20,  # 4개가 나올 확률 20%
            5: 10   # 5개가 나올 확률 10%
        }
    }
}

def show_inventory():
    """인벤토리의 내용을 보여주는 함수"""
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for mineral, count in data.items():
        if count > 0:
            print(f"{mineral}: {count}개")

def show_user_info():
    """사용자 정보를 보여주는 함수"""
    user_data = load_user_data()
    print("=== 내 정보 ===")
    print(f"총 채굴 횟수: {user_data['채굴횟수']}회")
    print("============")

def load_user_data():
    """사용자 데이터를 로드하는 함수"""
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 기본 사용자 데이터 생성
        default_data = {
            "채굴횟수": 0
        }
        with open('user_data.json', 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

def save_user_data(data):
    """사용자 데이터를 저장하는 함수"""
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def mine_mineral():
    """광물을 채굴하는 함수"""
    # 인벤토리 로드
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 채굴 실행
    mined = random.choices(item_mineral[:10], weights=item_prob[:10], k=1)[0]
    data[mined] += 1
    print(f"{mined} 1개를 채굴했습니다!")
    
    # 인벤토리 저장
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    # 채굴 횟수 증가
    user_data = load_user_data()
    user_data["채굴횟수"] += 1
    save_user_data(user_data)

def open_box(box_name, amount):
    """상자를 여는 함수
    
    Args:
        box_name (str): 열 상자의 이름
        amount (int): 열 상자의 개수
    """
    try:
        # 상자가 존재하는지 확인
        if box_name not in box_rewards:
            print(f"존재하지 않는 상자입니다. 열 수 있는 상자: {', '.join(box_rewards.keys())}")
            return

        # 인벤토리 데이터 로드
        with open('inven.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 상자가 충분한지 확인
        if data.get(box_name, 0) < amount:
            print(f"{box_name}이(가) 부족합니다. 필요: {amount}개, 보유: {data.get(box_name, 0)}개")
            return
        
        # 상자 소비
        data[box_name] -= amount
        
        # 보상 지급
        rewards = {}
        box_info = box_rewards[box_name]
        
        for _ in range(amount):
            # 아이템 선택
            item = random.choices(box_info["아이템"], weights=box_info["확률"], k=1)[0]
            # 개수 결정 (확률에 따라)
            counts = list(box_info["개수"].keys())
            weights = list(box_info["개수"].values())
            count = random.choices(counts, weights=weights, k=1)[0]
            
            if item not in rewards:
                rewards[item] = 0
            rewards[item] += count
            
            # 인벤토리에 추가
            if item not in data:
                data[item] = 0
            data[item] += count
        
        # 인벤토리 저장
        with open('inven.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 결과 출력
        print(f"{box_name} {amount}개를 열었습니다!")
        print("획득한 아이템:")
        for item, count in rewards.items():
            print(f"- {item} {count}개")
            
    except Exception as e:
        print("상자를 여는 중 오류가 발생했습니다.")

def craft_item(item_name, amount):
    """아이템을 제작하는 함수
    
    Args:
        item_name (str): 제작할 아이템 이름
        amount (int): 제작할 개수
    """
    try:
        # 제작 가능한 아이템인지 확인
        if item_name not in recipes:
            print(f"제작할 수 없는 아이템입니다. 제작 가능한 아이템: {', '.join(recipes.keys())}")
            return

        # 인벤토리 데이터 로드
        with open('inven.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 재료가 충분한지 확인
        can_craft = True
        required_materials = {}
        for material, required_amount in recipes[item_name].items():
            required_materials[material] = required_amount * amount
            if data.get(material, 0) < required_materials[material]:
                can_craft = False
                print(f"{material}이(가) 부족합니다. 필요: {required_materials[material]}개, 보유: {data.get(material, 0)}개")
        
        # 제작 실행
        if can_craft:
            # 재료 소비
            for material, req_amount in required_materials.items():
                data[material] -= req_amount
            
            # 결과물 추가
            if item_name not in data:
                data[item_name] = 0
            data[item_name] += amount
            
            # 인벤토리 저장
            with open('inven.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f"{item_name} {amount}개를 제작했습니다!")
    except Exception as e:
        print("제작 중 오류가 발생했습니다.")

cmd = input('명령을 입력하세요: ')

#----------------------------명령어 처리--------------------------------------------------

if cmd == "ㅇ인벤토리 광물":
    show_inventory()
elif cmd == "ㅇ채굴":
    mine_mineral()
elif cmd.startswith("ㅇ제작 "):
    parts = cmd.split()
    if len(parts) != 3:
        print("올바른 형식: ㅇ제작 {아이템이름} {개수}")
    else:
        try:
            item_name = parts[1]
            amount = int(parts[2])
            craft_item(item_name, amount)
        except ValueError:
            print("개수는 숫자여야 합니다.")
elif cmd.startswith("ㅇ상자열기 "):
    parts = cmd.split()
    if len(parts) != 3:
        print("올바른 형식: ㅇ상자열기 {상자이름} {개수}")
    else:
        try:
            box_name = parts[1]
            amount = int(parts[2])
            open_box(box_name, amount)
        except ValueError:
            print("개수는 숫자여야 합니다.")
elif cmd == "ㅇ내정보":
    show_user_info()
