from urllib.request import urlopen, Request
from pprint import pprint
import json
import time
import numpy as np
warframe_market_api_base_url = 'https://api.warframe.market/v1/items'
warframe_drop_data_url = 'http://drops.warframestat.us/data'
ERA_LITH = 'Lith'
ERA_MESO = 'Meso'
ERA_NEO = 'Neo'
ERA_AXI = 'Axi'
FORMA = 'Forma'
MISSION_ROTATION_A = 'A'
MISSION_ROTATION_B = 'B'
MISSION_ROTATION_C = 'C'
MISSION_ROTATIONS = [MISSION_ROTATION_A, MISSION_ROTATION_B, MISSION_ROTATION_C]
RELIC_TIER0 = 'Intact'
RELIC_TIER1 = 'Exceptional'
RELIC_TIER2 = 'Flawless'
RELIC_TIER3 = 'Radiant'
RELIC_TIERS = [RELIC_TIER0, RELIC_TIER1, RELIC_TIER2, RELIC_TIER3]
ERAS = [ERA_LITH, ERA_MESO, ERA_NEO, ERA_AXI]

ORDER_SELL = 'sell'
ORDER_BUY = 'buy'
requests = 0


loaded_prices = {}

def is_relic(str):
	split_str = str.split(' ')
	return 'Relic' in split_str


def get_drop_data(url_extension):
	url = '{}{}'.format(warframe_drop_data_url, url_extension)
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_data = urlopen(req).read()
	return json.loads(url_data)

def get_all_missions():
	all_data = get_drop_data('/missionRewards.json')['missionRewards']
	return all_data

def _filter_order(order):
	order.pop('creation_date')
	order.pop('id')
	order.pop('last_update')
	order.pop('visible')
	order['user'].pop('avatar')
	order['user'].pop('id')
	order['user'].pop('last_seen')
	order['user'].pop('reputation')
	order['user'].pop('reputation_bonus')
	return order

def get_all_items():
	req = Request(warframe_market_api_base_url)
	data = json.loads(urlopen(req).read())['payload']['items']['en']
	for item in data:
		item.pop('id')
	return data

all_items = get_all_items()
star_chart = get_all_missions()
all_relics = get_drop_data('/relics.json')

def _encode(string):
	for item in all_items:
		if item['item_name'] == string:
			return item['url_name']
	return string.lower().replace(' ', '_').replace('&', 'and').replace('_blueprint', '')

def _decode(string):
	return string.title().replace('_', ' ').replace('and', '&')

def find_relic_rewards(relic_era, relic_name, relic_tier=RELIC_TIER0):
	relics = list(filter(lambda relic: relic['tier'] == relic_era 
								   and relic['relicName'] == relic_name
								   and relic['state'] == relic_tier, all_relics['relics']))
	return_data = relics[0]['rewards']
	return return_data




class PrimePart:
	def __init__(self, name, drop_chance=100):
		self.name = _decode(name)
		self.url_name = _encode(name)
		self.drop_chance = drop_chance
		self.price = None
		self.isForma = False

	def load_price(self):
		if not self.isForma:
			if loaded_prices.get(self.url_name):
				self.price = loaded_prices.get(self.url_name)

			else:
				url = f'{warframe_market_api_base_url}/{self.url_name}/orders'
				req = Request(url)
				orders = json.loads(urlopen(req).read())['payload']['orders']
				global requests
				requests += 1

				#filters orders
				orders = list(map(_filter_order, orders))
				orders = list(filter(lambda order: order['order_type'] == ORDER_SELL.lower(), orders))
				orders = list(filter(lambda order: order['platform'] == 'pc', orders))
				orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))
				prices = list(map(lambda order: order['platinum'], orders))
				self.price = prices[np.argmin(prices)]
				loaded_prices[self.url_name] = self.price
		else:
			self.price = 10

	def _parse(self):
		return_data = {}
		return_data['name'] = self.name
		return_data['url_name'] = self.url_name
		return_data['price'] = self.price
		return return_data




class Forma(PrimePart):
	def __init__(self, drop_chance=100):
		PrimePart.__init__(self, FORMA, drop_chance)
		self.name = FORMA
		self.price = 10
		self.isForma = True


class Relic:
	def __init__(self, era, name, drop_chance=100, relic_tier=RELIC_TIER0):
		self.era = era
		self.name = _encode(name)
		self.url_name = _decode(name)
		self.average_price = None
		self.drop_chance = drop_chance
		self.relic_tier = relic_tier

		rewards = find_relic_rewards(self.era.capitalize(), 
									 self.url_name.capitalize(),
									 self.relic_tier)
		self.rewards = []
		for reward in rewards:
			split_name = reward['itemName'].lower().split(' ')
			if 'forma' in split_name:
				self.rewards.append(Forma(reward['chance']))
			else:
				self.rewards.append(PrimePart(reward['itemName'], reward['chance']))

	def load_price(self):
		self.average_price = 0
		for item in self.rewards:
			item.load_price()
			price = item.price * item.drop_chance / 100
			self.average_price += price
		self.average_price = round(self.average_price, 2)


	def _parse(self):
		return_data = {}
		return_data['relic_era'] = self.era
		return_data['relic_name'] = self.name
		return_data['average_price'] = self.average_price
		return_data['rewards'] = []
		for reward in self.rewards:
			return_data['rewards'].append(reward._parse())
		return return_data


class Rotation:
	def __init__(self, rotation, rewards, relic_tier=RELIC_TIER0):
		self.type = rotation
		rewards = list(filter(lambda reward: 'Relic' in reward['itemName'].split(' '), rewards))
		self.rewards = []
		self.average_price = None

		for relic in rewards:
			split_name = relic['itemName'].split(' ')
			relic_era = split_name[0]
			relic_name = split_name[1]
			self.rewards.append(Relic(relic_era, relic_name, relic['chance'], relic_tier))

	def load_average_price(self):
		if not self.average_price:
			self.average_price = 0
			for relic in self.rewards:
				relic.load_price()
				price = relic.average_price * relic.drop_chance / 100
				self.average_price += price
			self.average_price = round(self.average_price, 2)

	def _parse(self):
		return_data = {}
		return_data['rotation_type'] = self.type
		return_data['average_price'] = self.average_price
		return_data['rewards'] = []
		for relic in self.rewards:
			return_data['rewards'].append(relic._parse())
		return return_data


class Mission:
	def __init__(self, planet, name, relic_tier=RELIC_TIER0):
		self.planet = planet.title()
		self.name = name.title()
		self.rotations = []

		rewards = star_chart[self.planet][self.name]['rewards']
		if type(rewards) == dict:
			for rotation in rewards:
				self.rotations.append(Rotation(rotation, rewards[rotation]))
		else:
			for rotation in rewards:
				self.rotations.append(Rotation(rotation, rewards))

	def load_average_price(self):
		for rotation in self.rotations:
			rotation.load_average_price()

	def _parse(self):
		return_data = {}
		return_data['planet'] = self.planet
		return_data['name'] = self.name
		return_data['rotations'] = []
		for rotation in self.rotations:
			return_data['rotations'].append(rotation._parse())

		return return_data

	def save(self):
		with open(f'missions/{self.planet}-{self.name}.json', 'w') as f:
			json.dump(self._parse(), f)

		



