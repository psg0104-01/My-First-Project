import json
import random
import os
import time
import sys

# 자원 목록 정의
item_mineral = ["돌", "주석", "철", "은", "금", "티타늄", "에메랄드", "루비", "사파이어", "다이아몬드", "방사능", "토륨", "라듐"]

# 상자 목록 정의
item_boxes = ["방사능상자"]

# 확률 정의 (자원 개수와 맞춰야 함)
item_prob = [3700, 1700, 1300, 1000, 800, 500, 400, 100, 200, 50, 250]
if len(item_mineral) != len(item_prob):
    item_prob = [1] * len(item_mineral)

# 제작 레시피 정의
recipes = {
    # 양식 : "아이템이름": {"재료1": 개수1, "재료2": 개수2, ...}
    "방사능상자": {"방사능": 3},
    # 곡괭이 제작 레시피
    "깨진곡괭이": {"돌": 2},
    "철곡괭이": {"철": 5, "주석": 2},
    "금곡괭이": {"금": 2, "티타늄": 2}
}

# 자동 동기화: 레시피에 새 아이템을 추가하면 해당 아이템을
# 채굴/인벤토리 목록에 자동으로 등록하고 확률 리스트(item_prob)를
# 맞춰줍니다. (간단한 기본 가중치 1을 추가)
def sync_recipes_into_items():
    """
    recipes의 키들을 검사하여 item_mineral, item_boxes, item_prob에
    자동으로 등록합니다.
    - 새 아이템은 item_mineral에 추가됩니다.
    - 이름이 '상자'로 끝나면 item_boxes에도 추가됩니다.
    - item_prob 길이가 item_mineral과 달라지면 기본 가중치 1을 추가합니다.
    """
    # 추가될 항목을 모아 한 번에 처리
    added = False
    for recipe_item in list(recipes.keys()):
        if recipe_item not in item_mineral:
            item_mineral.append(recipe_item)
            # 기본 가중치 추가
            item_prob.append(1)
            added = True
        # 이름에 '상자'가 포함되면 상자 목록에도 추가 (중복 방지)
        if recipe_item not in item_boxes and recipe_item.endswith('상자'):
            item_boxes.append(recipe_item)
            added = True

    # 안전 점검: 길이 불일치 시 item_prob을 item_mineral 길이에 맞춤
    if len(item_prob) != len(item_mineral):
        # 확률 리스트가 짧으면 1로 채우고, 길면 잘라냄
        if len(item_prob) < len(item_mineral):
            item_prob.extend([1] * (len(item_mineral) - len(item_prob)))
        else:
            del item_prob[len(item_mineral):]
        added = True

    if added:
        # 간단한 로그 출력 (개발 중 도움용)
        # 실제 배포에서는 print를 제거하거나 로거로 대체하세요.
        print("recipes 항목을 item_mineral/item_boxes/item_prob에 동기화했습니다.")

# recipes로 추가된 아이템을 위 목록에 반영
sync_recipes_into_items()

# 곡괭이(도구) 정의: 이름 -> 속성
# cooldown: 채굴 쿨타임(초), drops: 한 번 채굴 시 드롭 개수
pickaxes = {
    # 기본 쿨타임은 120초 (깨진곡괭이 기준). 다른 곡괭이는 더 나은 기본값을 가질 수 있음.
    "깨진곡괭이": {"cooldown": 120.0, "drops": 1},
    "철곡괭이": {"cooldown": 90.0, "drops": 10},
    "금곡괭이": {"cooldown": 60.0, "drops": 2}
}

# 상점 아이템 목록: (이름, 구매가)
shop_items = [
    ("깨진곡괭이", 500),
    ("철곡괭이", 50000),
    ("금곡괭이", 100000),
    ("강화권", 1000000)  # 구매 시 장착한 곡괭이의 +1강 적용
]

# (업그레이드 시스템 제거)
# 과거에는 곡괭이를 다른 등급으로 재료로 업그레이드하는 시스템이 있었으나
# 요구사항에 따라 업그레이드는 지원하지 않습니다. 대신 `ㅇ강화`로 레벨(+강)만 올릴 수 있습니다.

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

    # 곡괭이 먼저 출력 (정해진 pickaxes 순서)
    printed = set()
    for pk in pickaxes.keys():
        if data.get(pk, 0) > 0:
            print(f"{pk}: {data.get(pk)}개")
            printed.add(pk)

    # 상자 출력
    for bx in item_boxes:
        if data.get(bx, 0) > 0:
            print(f"{bx}: {data.get(bx)}개")
            printed.add(bx)

    # 나머지 아이템 출력
    for mineral, count in data.items():
        if mineral in printed:
            continue
        if count > 0:
            print(f"{mineral}: {count}개")

def show_user_info():
    """사용자 정보를 보여주는 함수"""
    user_data = load_user_data()
    print("=== 내 정보 ===")
    print(f"총 채굴 횟수: {user_data['채굴횟수']}회")
    print(f"골드: {user_data.get('골드', 0)}")
    equipped = user_data.get('equipped_pickaxe', '없음')
    print(f"장착 곡괭이: {equipped}")
    level = user_data.get('pickaxe_enhance', {}).get(equipped, 0)
    print(f"현재 강화: +{level}강")
    settings = user_data.get('enhance_settings', {'cooldown': 0.2, 'extra_drops': 0.1})
    print(f"강화 효과(레벨당): 쿨감 {settings.get('cooldown')}초, 추가드롭비율 {settings.get('extra_drops')}")
    print("============")

def load_user_data():
    """사용자 데이터를 로드하는 함수"""
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 기본 사용자 데이터 생성
        default_data = {
            "채굴횟수": 0,
            # 장비로 사용할 곡괭이 이름
            "equipped_pickaxe": "깨진곡괭이",
            # 플레이어 골드 (상점 판매에 사용)
            "골드": 0,
            # 마지막 채굴 시각 (time.time())
            "last_mine_time": 0.0,
            # 곡괭이 강화 레벨들 (이름 -> level)
            "pickaxe_enhance": {},
            # 강화 설정: per-level cooldown 감소(초), per-level 추가 드롭 비율
            # 기본값: 레벨당 쿨타임 -10초, 레벨당 추가드롭비율 0.2
            "enhance_settings": {"cooldown": 10.0, "extra_drops": 0.2}
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

    # 사용자 데이터 및 장비 정보
    user_data = load_user_data()
    equipped = user_data.get('equipped_pickaxe', '깨진곡괭이')
    pick = pickaxes.get(equipped, pickaxes['깨진곡괭이'])

    # 강화 레벨 적용
    enhance_levels = user_data.get('pickaxe_enhance', {})
    level = enhance_levels.get(equipped, 0)
    settings = user_data.get('enhance_settings', {"cooldown": 0.2, "extra_drops": 0.1})

    # 쿨타임 계산 (기본 쿨타임 - level * 설정)
    now = time.time()
    last = user_data.get('last_mine_time', 0.0)
    base_cooldown = pick.get('cooldown', 5.0)
    cooldown_reduction = level * settings.get('cooldown', 0.2)
    # 최소 쿨타임은 30초로 제한
    effective_cooldown = max(30.0, base_cooldown - cooldown_reduction)
    if now - last < effective_cooldown:
        remain = effective_cooldown - (now - last)
        print(f"아직 쿨타임입니다. 남은시간: {remain:.1f}초")
        return

    # 드롭 개수 계산 (기본 drops + floor(level * extra_drops))
    base_drops = pick.get('drops', 1)
    extra_per_level = settings.get('extra_drops', 0.1)
    extra_drops = int(level * extra_per_level)
    drops = base_drops + extra_drops

    # 드롭 실행
    mined_items = random.choices(item_mineral, weights=item_prob, k=drops)

    # 인벤토리에 추가
    rewards_summary = {}
    for mined in mined_items:
        if mined not in data:
            data[mined] = 0
        data[mined] += 1
        rewards_summary[mined] = rewards_summary.get(mined, 0) + 1

    # 인벤토리 저장
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 채굴 횟수 증가 및 쿨타임 갱신
    user_data["채굴횟수"] += 1
    user_data['last_mine_time'] = now
    save_user_data(user_data)

    # 결과 출력
    total_drops = sum(rewards_summary.values())
    print(f"{equipped}(+{level}강)으로 채굴하여 {total_drops}개를 획득했습니다!")
    for m, c in rewards_summary.items():
        print(f"- {m} {c}개")

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

def equip_pickaxe(pickaxe_name):
    """곡괭이를 장착하는 함수 (인벤토리에서 존재해야 함)"""
    try:
        with open('inven.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get(pickaxe_name, 0) <= 0:
            print(f"{pickaxe_name}이(가) 인벤토리에 없습니다.")
            return

        user_data = load_user_data()
        user_data['equipped_pickaxe'] = pickaxe_name
        save_user_data(user_data)
        print(f"{pickaxe_name}을(를) 장착했습니다.")
    except Exception:
        print("장착 중 오류가 발생했습니다.")

def sell_pickaxe(pickaxe_name, amount):
    """곡괭이 판매는 불가능합니다. 곡괭이는 판매할 수 없습니다."""
    print("곡괭이는 판매할 수 없습니다.")


# 광물/상자 등의 아이템을 판매하는 함수 (곡괭이는 제외)
mineral_sell_prices = {
    # 예시 가격 (골드)
    "돌": 1000,
    "주석": 1500,
    "철": 4000,
    "은": 10000,
    "금": 30000,
    "티타늄": 50000,
    "에메랄드": 100000,
    "루비": 150000,
    "사파이어": 170000,
    "다이아몬드": 250000,
    # 토륨과 방사능상자는 판매 불가로 둡니다 (가격 미등록 => 판매 불가)
}

def sell_item(item_name, amount):
    """아이템을 판매해서 골드를 얻는 함수 (곡괭이 제외)"""
    try:
        if item_name in pickaxes:
            print("곡괭이는 판매할 수 없습니다.")
            return

        with open('inven.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get(item_name, 0) < amount:
            print(f"{item_name}이(가) 부족합니다. 보유: {data.get(item_name,0)}개")
            return

        price = mineral_sell_prices.get(item_name)
        if price is None:
            print("이 아이템은 판매 불가합니다.")
            return

        data[item_name] -= amount
        gain = price * amount
        user_data = load_user_data()
        user_data['골드'] = user_data.get('골드', 0) + gain

        with open('inven.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        save_user_data(user_data)

        print(f"{item_name} {amount}개를 판매하여 골드 {gain}을(를) 획득했습니다.")
    except Exception:
        print("판매 중 오류가 발생했습니다.")

def strengthen_pickaxe():
    """장비 업그레이드는 이 시스템에서 지원하지 않습니다.

    요구사항에 따라 '업그레이드(다른 등급으로 변경)'는 제공되지 않습니다.
    대체로 사용 가능한 기능은 'ㅇ강화'로 레벨(+강)만 올리는 것입니다.
    """
    print("곡괭이 업그레이드는 지원하지 않습니다. 'ㅇ강화' 명령으로 레벨을 올리세요.")

def enhance_level_up(target_pickaxe=None):
    """특정 곡괭이(또는 장착중인 곡괭이)의 강화 레벨을 1 올리는 함수.

    Args:
        target_pickaxe (str|None): 강화할 곡괭이 이름. None이면 장착중인 곡괭이를 강화.
    """
    try:
        user_data = load_user_data()

        # 대상 곡괭이 결정: 인자로 주어진 이름 우선, 없으면 장착 중인 곡괭이
        if target_pickaxe:
            # 인벤토리에 해당 곡괭이가 있는지 확인(소유 여부)
            with open('inven.json', 'r', encoding='utf-8') as f:
                inven = json.load(f)
            if inven.get(target_pickaxe, 0) <= 0:
                print(f"{target_pickaxe}을(를) 소유하고 있지 않습니다. 먼저 해당 곡괭이를 획득하세요.")
                return
            equipped = target_pickaxe
        else:
            equipped = user_data.get('equipped_pickaxe', '깨진곡괭이')

        levels = user_data.get('pickaxe_enhance', {})
        current = levels.get(equipped, 0)
        settings = user_data.get('enhance_settings', {'cooldown': 10.0, 'extra_drops': 0.2, 'max_level': 10})
        max_level = settings.get('max_level', 10)
        if current >= max_level:
            print(f"이미 {max_level}강입니다. 더 이상 강화할 수 없습니다.")
            return

        # 비용 산정 (조정 가능)
        cost = 100 * (current + 1)
        gold = user_data.get('골드', 0)
        if gold < cost:
            print(f"골드가 부족합니다. 필요: {cost}골드, 보유: {gold}골드")
            print("광물을 `ㅇ판매 {아이템} {개수}`로 판매하여 골드를 획득하세요.")
            return

        # 골드 차감 및 레벨 업
        user_data['골드'] = gold - cost
        current += 1
        levels[equipped] = current
        user_data['pickaxe_enhance'] = levels
        save_user_data(user_data)
        print(f"{equipped}이(가) +{current}강이 되었습니다! (소모 골드: {cost})")
    except Exception:
        print("강화 중 오류가 발생했습니다.")

def set_enhance_settings(cooldown_reduction, extra_drops_per_level, max_level=None):
    """강화시 레벨당 성능 증가량을 설정하는 함수

    Args:
        cooldown_reduction (float): 레벨당 쿨타임 감소(초)
        extra_drops_per_level (float): 레벨당 추가 드롭 비율(예: 0.1은 10레벨에 +1드롭)
        max_level (int, optional): 최대 강화 레벨. None이면 기존값 유지.
    """
    try:
        user_data = load_user_data()
        # preserve existing max_level if not provided
        existing_max = user_data.get('enhance_settings', {}).get('max_level', 10)
        if max_level is None:
            final_max = existing_max
        else:
            try:
                final_max = int(max_level)
            except Exception:
                print("max_level은 정수여야 합니다.")
                return

        user_data['enhance_settings'] = {"cooldown": float(cooldown_reduction), "extra_drops": float(extra_drops_per_level), "max_level": final_max}
        save_user_data(user_data)
        print(f"강화 설정이 저장되었습니다. 쿨감: {cooldown_reduction}s, 추가드롭비율: {extra_drops_per_level}, 최대강: +{final_max}")
    except Exception:
        print("설정 저장 중 오류가 발생했습니다.")

def show_shop():
    """상점(구매 목록) 출력 (번호 입력으로 구매)"""
    print("=== 상점 ===")
    for idx, (name, price) in enumerate(shop_items, start=1):
        print(f"{idx}. {name} - 구매가 {price} 골드")
    user_data = load_user_data()
    print(f"보유 골드: {user_data.get('골드',0)}")

def buy_from_shop(index):
    """상점 번호로 아이템을 구매하는 함수

    Args:
        index (int): 1-based 상점 아이템 번호
    """
    try:
        if index < 1 or index > len(shop_items):
            print("존재하지 않는 상점 아이템 번호입니다.")
            return
        name, price = shop_items[index-1]
        user_data = load_user_data()
        gold = user_data.get('골드', 0)
        if gold < price:
            print(f"골드가 부족합니다. 필요: {price}골드, 보유: {gold}골드")
            return

        # 인벤토리에 추가
        # 골드 차감
        user_data['골드'] = gold - price

        # 특별 아이템 처리: '강화권'은 구매 즉시 장착된 곡괭이 +1강 적용
        if name == "강화권":
            levels = user_data.get('pickaxe_enhance', {})
            equipped = user_data.get('equipped_pickaxe', '깨진곡괭이')
            settings = user_data.get('enhance_settings', {})
            max_level = settings.get('max_level', 10)
            current = levels.get(equipped, 0)
            if current >= max_level:
                print(f"이미 {max_level}강입니다. 더 이상 강화할 수 없습니다. (구매는 취소되지 않음)")
            else:
                current += 1
                levels[equipped] = current
                user_data['pickaxe_enhance'] = levels
                print(f"{equipped}이(가) +{current}강이 되었습니다! (강화권 사용)")

        else:
            # 일반 아이템은 인벤토리에 추가
            with open('inven.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            data[name] = data.get(name, 0) + 1
            with open('inven.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        save_user_data(user_data)
        print(f"{name}을(를) 구매했습니다. -{price}골드")
    except Exception:
        print("구매 중 오류가 발생했습니다.")

# 명령을 커맨드라인 인수로 받을 수 있게 변경 (자동화/테스트용).
# 예: python main.py ㅇ제작 방사능상자 1
if len(sys.argv) > 1:
    cmd = ' '.join(sys.argv[1:])
else:
    cmd = input('명령을 입력하세요: ')

#----------------------------명령어 처리--------------------------------------------------

if cmd == "ㅇ인벤토리 광물":
    show_inventory()
elif cmd == "ㅇ채굴":
    mine_mineral()
elif cmd.startswith("ㅇ제작 "):
    parts = cmd.split()
    # 아이템 이름에 공백이 포함될 수 있으므로 마지막 토큰을 개수로 취급
    if len(parts) < 3:
        print("올바른 형식: ㅇ제작 {아이템이름} {개수}")
    else:
        try:
            amount = int(parts[-1])
            item_name = ' '.join(parts[1:-1])
            craft_item(item_name, amount)
        except ValueError:
            print("개수는 숫자여야 합니다.")
elif cmd.startswith("ㅇ상자열기 "):
    parts = cmd.split()
    # 상자 이름에 공백이 있을 수 있으므로 마지막 토큰을 개수로 처리
    if len(parts) < 3:
        print("올바른 형식: ㅇ상자열기 {상자이름} {개수}")
    else:
        try:
            amount = int(parts[-1])
            box_name = ' '.join(parts[1:-1])
            open_box(box_name, amount)
        except ValueError:
            print("개수는 숫자여야 합니다.")
elif cmd == "ㅇ내정보":
    show_user_info()
elif cmd.startswith("ㅇ장착 "):
    parts = cmd.split()
    if len(parts) != 2:
        print("올바른 형식: ㅇ장착 {곡괭이이름}")
    else:
        equip_pickaxe(parts[1])
elif cmd.startswith("ㅇ곡괭이판매 "):
    print("곡괭이는 판매할 수 없습니다. 곡괭이는 판매 불가합니다.")
elif cmd.startswith("ㅇ판매 "):
    parts = cmd.split()
    if len(parts) != 3:
        print("올바른 형식: ㅇ판매 {아이템이름} {개수}")
    else:
        try:
            sell_item(parts[1], int(parts[2]))
        except ValueError:
            print("개수는 숫자여야 합니다.")
elif cmd == "ㅇ곡괭이강화":
    strengthen_pickaxe()
elif cmd.startswith("ㅇ강화"):
    parts = cmd.split()
    # 사용법: 'ㅇ강화' -> 장착중인 곡괭이 강화, 'ㅇ강화 {곡괭이이름}' -> 해당 곡괭이 강화(보유 필요)
    if len(parts) == 1:
        enhance_level_up()
    else:
        enhance_level_up(parts[1])
elif cmd.startswith("ㅇ강화설정 "):
    parts = cmd.split()
    # 확장: ㅇ강화설정 {쿨감} {추가드롭비율} [최대강]
    if len(parts) not in (3, 4):
        print("올바른 형식: ㅇ강화설정 {쿨타임감소(초)} {추가드롭비율} [최대강]")
    else:
        try:
            cd = float(parts[1])
            extra = float(parts[2])
            if len(parts) == 4:
                maxl = int(parts[3])
                set_enhance_settings(cd, extra, maxl)
            else:
                set_enhance_settings(cd, extra)
        except ValueError:
            print("숫자 형식이 올바르지 않습니다.")
elif cmd == "ㅇ상점":
    show_shop()
elif cmd.startswith("ㅇ구매 "):
    parts = cmd.split()
    if len(parts) != 2:
        print("올바른 형식: ㅇ구매 {상점의 아이템 번호}")
    else:
        try:
            idx = int(parts[1])
            buy_from_shop(idx)
        except ValueError:
            print("아이템 번호는 숫자여야 합니다.")
