import json
import random
import os
import time
import sys

# 상자 종류
box_kind = ["기본상자", "희귀상자" , "강화상자" , "특수상자" ,  "전설상자" ,  "AIO상자",  "신화상자" , "NEXT상자"]


def _weighted_choice(weight_map):
	"""Choose a key from weight_map (key->weight) using weights.

	Returns the selected key.
	"""
	total = sum(weight_map.values())
	if total <= 0:
		raise ValueError("Total weight must be positive")
	r = random.uniform(0, total)
	upto = 0
	for k, w in weight_map.items():
		upto += w
		if r <= upto:
			return k
	# Fallback
	return next(iter(weight_map))


# Simple drop tables for demonstration. Expand as needed.
_drops = {
	"common": ["동전", "회복포션", "일반강화석"],
	"rare": ["희귀무기", "희귀방어구", "희귀장비상자"],
	"epic": ["강화무기", "강화방어구"],
	"legend": ["전설무기", "전설장비"],
	"mythic": ["신화검", "신화방패"],
	"aio": ["AIO모듈", "AIO칩"],
	"next": ["NEXT장비", "NEXT코어"]
}

# rarity weight distributions per box type (weights sum not required; any positive weights OK)
_box_rarity_weights = {
	"기본상자": {"common": 80, "rare": 15, "epic": 4, "legend": 1},
	"희귀상자": {"common": 50, "rare": 35, "epic": 12, "legend": 3},
	"강화상자": {"common": 40, "rare": 30, "epic": 20, "legend": 9, "mythic": 1},
	"특수상자": {"common": 30, "rare": 30, "epic": 25, "legend": 10, "mythic": 4, "aio": 1},
	"전설상자": {"rare": 30, "epic": 30, "legend": 30, "mythic": 9, "aio": 1},
	"AIO상자": {"aio": 60, "epic": 20, "legend": 15, "mythic": 5},
	"신화상자": {"legend": 30, "mythic": 60, "aio": 5, "next": 5},
	"NEXT상자": {"next": 70, "mythic": 20, "legend": 10}
}


def open_box(kind, inventory=None):
	"""Open a box of type `kind` and update inventory.

	Args:
	  kind (str): one of the names in `box_kind`.
	  inventory (dict, optional): mapping item_name -> qty. If None, a new dict is created.

	Returns:
	  tuple: (item_name, rarity, qty, inventory)

	Raises:
	  ValueError: if `kind` is not a valid box name.

	Behavior:
	  - Selects a rarity based on the box's configured weights.
	  - Chooses a random item from that rarity's drop list.
	  - For "동전" (coins) gives a random qty; otherwise qty is 1.
	"""
	if kind not in _box_rarity_weights:
		raise ValueError(f"알 수 없는 상자 종류: {kind}")

	if inventory is None:
		inventory = {}

	weights = _box_rarity_weights[kind]
	rarity = _weighted_choice(weights)

	items = _drops.get(rarity)
	if not items:
		# fallback to common
		items = _drops["common"]

	item = random.choice(items)

	# quantity logic
	if item == "동전":
		qty = random.randint(50, 500)
	else:
		qty = 1

	inventory[item] = inventory.get(item, 0) + qty

	return item, rarity, qty, inventory


if __name__ == "__main__":
	# non-interactive demo: open a few boxes and print results
	demo_inventory = {}
	print("상자 목록:")
	for i, b in enumerate(box_kind, 1):
		print(f"  {i}. {b}")

	print("\n데모: 무작위로 5개의 상자를 열어봅니다...\n")
	for i in range(5):
		kind = random.choice(box_kind)
		item, rarity, qty, demo_inventory = open_box(kind, demo_inventory)
		print(f"[{i+1}] {kind} => {item} (등급: {rarity}, 수량: {qty})")

	print("\n최종 인벤토리:")
	print(json.dumps(demo_inventory, ensure_ascii=False, indent=2))

