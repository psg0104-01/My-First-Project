import json
import random


# inven.json의 key를 항상 item_mineral로 사용
try:
    with open('inven.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # inven.json이 없으면 기본 자원 목록 사용
    item_mineral = ["돌", "주석", "철", "은", "금", "티타늄", "에메랄드", "루비", "사파이어", "다이아몬드", "방사능"]
    data = {name: 0 for name in item_mineral}

# 확률도 자원 개수에 맞게 동기화 (없으면 균등 확률)
if len(item_mineral) == 11:
    item_prob = [3700, 1700, 1300, 1000, 800, 500, 400, 100, 200, 50, 250]
else:
    item_prob = [1] * len(item_mineral)




cmd = input('명령을 입력하세요: ')


if cmd == "ㅇ인벤토리 광물":
    for mineral, count in data.items():
        if count > 0:
            print(f"{mineral}: {count}개")




# 'ㅇ채굴' 명령 처리 (1개만 채굴)
if cmd == "ㅇ채굴":
    mined = random.choices(item_mineral, weights=item_prob, k=1)[0]
    data[mined] += 1
    print(f"{mined} 1개를 채굴했습니다!")
# JSON에 인벤토리 저장
with open('inven.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
