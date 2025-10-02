import json
import random

import os

# 자원 목록 정의 (상자류 포함)
item_mineral = ["돌", "주석", "철", "은", "금", "티타늄", "에메랄드", "루비", "사파이어", "다이아몬드", "방사능", "토륨", "라듐", "방사능상자"]

# 확률 정의 (자원 개수와 맞춰야 함)
item_prob = [3700, 1700, 1300, 1000, 800, 500, 400, 100, 200, 50, 250]
if len(item_mineral) != len(item_prob):
    item_prob = [1] * len(item_mineral)

# 인벤토리 불러오기 또는 초기화
if os.path.exists('inven.json'):
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 새 자원이 추가된 경우 0으로 추가
    for mineral in item_mineral:
        if mineral not in data:
            data[mineral] = 0
else:
    data = {name: 0 for name in item_mineral}


cmd = input('명령을 입력하세요: ')



if cmd == "ㅇ인벤토리 광물":
    # 항상 최신 데이터 반영
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for mineral, count in data.items():
        if count > 0:
            print(f"{mineral}: {count}개")

#----------------------------ㅇ채굴--------------------------------------------------

elif cmd == "ㅇ채굴":
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    mined = random.choices(item_mineral[:10], weights=item_prob[:10], k=1)[0]
    data[mined] += 1
    print(f"{mined} 1개를 채굴했습니다!")
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#----------------------------ㅇ제작 {아이템}--------------------------------------------------
elif cmd.startswith("ㅇ제작"):
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    parts = cmd.split()
    if len(parts) < 3:
        print("제작할 아이템 이름과 개수를 입력하세요.")
    else:
        item_name = parts[1]
        try:
            count = int(parts[2])
        except ValueError:
            print("개수는 숫자로 입력하세요.")
            count = 0
        if count < 1:
            print("개수는 1 이상이어야 합니다.")

#------------------------------방사능 상자(제작)------------------------------------------------

        elif item_name == "방사능상자":
            need = 10 * count
            if data["방사능"] >= need:
                data["방사능"] -= need
                if "방사능상자" not in data:
                    data["방사능상자"] = 0
                data["방사능상자"] += count
                print(f"방사능상자 {count}개를 제작했습니다! (보유 방사능상자: {data['방사능상자']})")
            else:
                print(f"방사능이 부족합니다. (필요: {need}개)")
        else:
            print(f"{item_name} 제작법이 없습니다.")
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#----------------------------ㅇ상자열기--------------------------------------------------

elif cmd.startswith("ㅇ상자열기"):
    with open('inven.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    parts = cmd.split()
    if len(parts) < 3:
        print("상자 이름과 개수를 입력하세요.")
    else:
        box_name = parts[1]
        try:
            count = int(parts[2])
        except ValueError:
            print("개수는 숫자로 입력하세요.")
            count = 0
        if count < 1:
            print("개수는 1 이상이어야 합니다.")
        elif box_name not in data or not box_name.endswith("상자"):
            print(f"{box_name}는(은) 존재하지 않는 상자입니다.")
        elif data[box_name] < count:
            print(f"{box_name}가 부족합니다. (보유: {data[box_name]})")

#------------------------------방사능 상자(열기)------------------------------------------------

        elif box_name == "방사능상자":
            data[box_name] -= count
            for _ in range(count):
                if box_name == "방사능상자":
                    rnd = random.randint(1, 100)
                    if rnd == 1:
                        data["토륨"] += 2
                        print("축하합니다! 토륨 2개를 획득했습니다!")
                    elif 2 <= rnd <= 11:
                        data["라듐"] += 3
                        print("라듐 3개를 획득했습니다!")
                    elif 12 <= rnd <= 25:
                        data["토륨"] += 1
                        print("토륨 1개를 획득했습니다!")
                    elif 26 <= rnd <= 55:
                        data["라듐"] += 1
                        print("라듐 1개를 획득했습니다!")
                    else:
                        print("꽝! 아무것도 얻지 못했습니다.")
                else:
                    print(f"{box_name}는 아직 열기 기능이 구현되지 않았습니다.")
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



