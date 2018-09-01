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
RELIC_TIER0 = 0
RELIC_TIER1 = 1
RELIC_TIER2 = 2
RELIC_TIER3 = 3
ERAS = [ERA_LITH, ERA_MESO, ERA_NEO, ERA_AXI]
ORDER_SELL = 'sell'
ORDER_BUY = 'buy'
def get_drop_data(url_extension, verbose=False):
	url = '{}{}'.format(warframe_drop_data_url, url_extension)
	if verbose:
		print('fetching {}'.format(url))
	start = time.time()
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_data = urlopen(req).read()
	end = time.time()
	if verbose:
		print('{} took {:0.2f} seconds'.format(url, end - start))
	return json.loads(url_data)

def _filter(order):
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
def encode(string):
	for item in all_items:
		if item['item_name'] == string:
			return item['url_name']
	return string.lower().replace(' ', '_').replace('&', 'and').replace('_blueprint', '')
		
def decode(string):
	return string.title().replace('_', ' ').replace('and', '&')

class Reward:
	def __init__(self, name):
		self.name = name
		self.price = None

class Forma(Reward):
	def __init__(self, drop_chance):
		Reward.__init__(self, FORMA)
		self.name = FORMA
		self.drop_chance = drop_chance
		self.price = None
		self.customer = None

	def get_price(self, _):
		self.price = 10

class PrimePart(Reward):
	def __init__(self, part_name, drop_chance):
		Reward.__init__(self, part_name)
		self.drop_chance = drop_chance
		drop_rates = [[]]
		self.name = decode(part_name)
		self.url_name = encode(part_name)


	def get_price(self, order_type, verbose=False):
		self.start_time = time.time()
		if not (order_type == ORDER_BUY or order_type == ORDER_SELL):
			raise ValueError('not a valid order type')
		#WORK DAME
		self.req = Request('{}/{}/orders'.format(warframe_market_api_base_url, self.url_name))
		self.orders = json.loads(urlopen(self.req).read())['payload']['orders']
		self.prices, self.customer_info = [], []

		#filters orders
		self.orders = list(map(_filter, self.orders))
		self.orders = list(filter(lambda order: order['order_type'] == order_type.lower(), self.orders))
		self.orders = list(filter(lambda order: order['platform'] == 'pc', self.orders))
		self.orders = list(filter(lambda order: order['user']['status'] == 'ingame', self.orders))

		self.prices = list(map(lambda order: order['platinum'], self.orders))
		self.customer_info = list(map(lambda order: {'username' : order['user']['ingame_name'], 
													 'region': order['user']['region']}, self.orders ))
		self.position = np.argmin(self.prices) if order_type == ORDER_SELL else np.argmax(self.prices)
		self.price = self.prices[self.position]
		self.customer = self.customer_info[self.position]
		self.end_time = time.time()
		if verbose:
			print('{} took {} seconds'.format(self.url_name, self.end_time - self.start_time))



class Relic:
	def __init__(self, relic_era, relic_name, drop_chance, verbose=False):
		if not relic_era in ERAS:
			raise ValueError('not a valid relic era')
		self.era = relic_era
		self.name = encode(relic_name)
		self.url_name = decode(relic_name)
		self.rewards = None
		self.drop_chance = drop_chance
		self.total_price = 0
	def load_rewards(self, verbose=False):
		self.start_time = time.time()
		self.raw_data = get_drop_data('/relics/{}/{}.json'.format(self.era.capitalize(),
																  self.url_name.capitalize()),
																  verbose=verbose)
		self.rewards = []
		for reward in self.raw_data['rewards']['Intact']:
			self.split_name = reward['itemName'].lower().split(' ')
			if 'forma' in self.split_name:
				self.rewards.append(Forma(reward['chance']))
			else:
				self.rewards.append(PrimePart(reward['itemName'], reward['chance']))
		self.end_time = time.time()
		if verbose:
			print('{} took {} seconds'.format(self.url_name, self.end_time - self.start_time))

	def get_sell_price(self, relic_tier):
		if relic_tier not in range(0, 4):
			raise ValueError('not a valid relic tier')
		for reward in self.rewards:
			reward.get_price(ORDER_SELL)
			self.total_price += reward.drop_chance / 100 * reward.price
class Mission:
	def __init__(self, mission_planet, mission_name):
		self.planet = mission_planet
		self.name = mission_name
		self.rewards = []
	def load_rewards(self, rotation):
		if not rotation in MISSION_ROTATIONS:
			raise ValueError('not a valid mission rotation')
		self.raw_data = get_drop_data('/missionRewards/{}/{}.json'.format(self.planet.capitalize(),
																		 self.name.capitalize()))['rewards'][rotation]
		self.raw_data = list(filter(lambda relic: 'Relic' in relic['itemName'].split(' '), self.raw_data))
		for relic in self.raw_data: 
			self.split_name = relic['itemName'].split(' ')
			self.rewards.append(Relic(self.split_name[0], self.split_name[1], relic['chance']))

	def get_reward_total_sell_price(self, rotation=MISSION_ROTATION_A, relic_tier=RELIC_TIER0):
		self.load_rewards(rotation)
		self.prices = []
		self.total_sell_price = 0
		for relic in self.rewards:
			relic.load_rewards() 
			relic.get_sell_price(relic_tier)
			#print(relic.drop_chance)
			self.prices.append({'era':relic.era,
							   'name': relic.name,
							   'total_price':relic.total_price})
			self.total_sell_price += relic.drop_chance / 100 * relic.total_price
		return self.total_sell_price


m = Mission('sedna', 'hydron')
print(m.get_reward_total_sell_price(rotation=MISSION_ROTATION_C, relic_tier=RELIC_TIER3))
