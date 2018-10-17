# TO DO:
# Make parsing missions contain relics' reward prices
#
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

def get_all_missions():
	missions = []
	all_data = get_drop_data('/missionRewards.json')['missionRewards']
	return all_data

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
star_chart = get_drop_data('/missionRewards.json')
all_relics = get_drop_data('/relics.json')

def encode(string):
	for item in all_items:
		if item['item_name'] == string:
			return item['url_name']
	return string.lower().replace(' ', '_').replace('&', 'and').replace('_blueprint', '')
		
def decode(string):
	return string.title().replace('_', ' ').replace('and', '&')

def request_orders(url_name):
	req = Request('{}/{}/orders'.format(warframe_market_api_base_url, url_name))
	orders = json.loads(urlopen(req).read())['payload']['orders']
	global requests
	requests = requests + 1
	return orders

def find_relic_rewards(relic_era, relic_name):
	relics = list(filter(lambda relic: relic['tier'] == relic_era and relic['relicName'] == relic_name, all_relics['relics']))
	return_data = {}
	for relic in relics:
		return_data[relic['state']] = relic['rewards']
	return return_data
class Reward:
	def __init__(self, name):
		self.name = name
		self.price = None


class Forma(Reward):
	def __init__(self, drop_chance):
		Reward.__init__(self, FORMA)
		self.name = FORMA
		self.url_name = FORMA
		self.drop_chance = drop_chance
		self.price = None
		self.customer = None

	def load_price(self, order_type, debug=False):
		self.price = 10
		if debug:
			print('forma')

class PrimePart(Reward):
	def __init__(self, part_name, drop_chance):
		Reward.__init__(self, part_name)
		self.drop_chance = drop_chance
		drop_rates = [[]]
		self.name = decode(part_name)
		self.url_name = encode(part_name)
		self.price = 0


	def load_price(self, order_type, debug=False):
		start_time = time.time()
		if not (order_type == ORDER_BUY or order_type == ORDER_SELL):
			raise ValueError('not a valid order type')
		orders = request_orders(self.url_name)
		prices, self.customer_info = [], []

		#filters orders
		orders = list(map(_filter, orders))
		orders = list(filter(lambda order: order['order_type'] == order_type.lower(), orders))
		orders = list(filter(lambda order: order['platform'] == 'pc', orders))
		orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))

		prices = list(map(lambda order: order['platinum'], orders))
		customer_info = list(map(lambda order: {'username' : order['user']['ingame_name'], 
													 'region': order['user']['region']}, orders ))
		position = np.argmin(prices) if order_type == ORDER_SELL else np.argmax(prices)
		self.price = prices[position]
		customer = customer_info[position]
		end_time = time.time()
		if debug:
			print('{} took {} seconds'.format(self.url_name, end_time - start_time))



class Relic:
	def __init__(self, relic_era, relic_name, drop_chance, verbose=False):
		if not relic_era in ERAS:
			raise ValueError('not a valid relic era')

		#initalize class variables
		self.era = relic_era
		self.name = encode(relic_name)
		self.url_name = decode(relic_name)
		self.rewards = {}
		self.drop_chance = drop_chance
		self.sell_price = {}

		# get relic drop rewards from the api
		start_time = time.time()
		rewards = find_relic_rewards(self.era.capitalize(), self.url_name.capitalize())
		for relic_tier in rewards:
			self.rewards[relic_tier] = []

			for reward in rewards[relic_tier]:
				split_name = reward['itemName'].lower().split(' ')
				if 'forma' in split_name:
					self.rewards[relic_tier].append(Forma(reward['chance']))
				else:
					self.rewards[relic_tier].append(PrimePart(reward['itemName'], reward['chance']))
		end_time = time.time()
		if verbose:
			print('{} took {} seconds'.format(self.url_name, end_time - start_time))


	def get_average_price(self, order_type, relic_tier, debug=False):
		average_price = 0
		if relic_tier not in RELIC_TIERS:
			raise ValueError('not a valid relic tier')

		for reward in self.rewards[relic_tier]:
			reward.load_price(order_type, debug=debug)
			average_price += reward.drop_chance / 100 * reward.price
		self.sell_price[relic_tier] = average_price
		return average_price

	def parse(self):
		'''returns the relic object into json format'''
		rewards = {}
		for tier in self.rewards:
			rewards[tier] = []
			for reward in self.rewards[tier]:
				rewards[tier].append({'name': reward.name,
								'url_name': reward.url_name,
								'drop_chance': reward.drop_chance,
								'average_sell_price': reward.price})
		data = {'name': self.name,
				'era': self.era,
				'url_name': self.url_name,
				'average_sell_price': self.sell_price,
				'relic_tiers': rewards}
		return data

class Mission:
	def __init__(self, mission_planet, mission_name, debug=False):
		# basic object variables

		self.planet = mission_planet.title()
		self.name = mission_name.title()
		self.total_sell_price = 0
		self.game_mode = None
		self.has_rotations = False
		self.prices_loaded = False
		print('initalizing {} {}'.format(self.planet.lower(), self.name.lower()))
		start_time = time.time()

		# TEMPORARY
		# loads rewards from all rotations
		#print(star_chart['missionRewards'][self.planet])
		if self.name == 'Stöfler':
			self.name = 'StöFler'
		data = star_chart['missionRewards'][self.planet][self.name]
		
		self.game_mode = data['gameMode']

		# filters out non-relic rewards
		filtered_rewards = {}
		if data['rewards'] == dict: 
			for rotation in data['rewards']:
				filtered_rewards[rotation] = list(filter(lambda relic: 'Relic' in relic['itemName'].split(' '), data['rewards'][rotation]))
		else:
			for rotation in data['rewards']:
				if filtered_rewards:
					filtered_rewards[rotation] = list(filter(lambda relic: 'Relic' in relic['itemName'].split(' '), data['rewards'][rotation]))
				else:
					print('error')
					break
		
		# initiates a relic object dictionary
		self.rewards = {}

		for rotation in filtered_rewards:
			self.rewards[rotation] = []
			print(rotation)
			for relic in filtered_rewards[rotation]:
				split_name = relic['itemName'].split(' ')
				relic_era = split_name[0]
				relic_name = split_name[1]
				relic = Relic(relic_era, relic_name, relic['chance'])
				self.rewards[rotation].append(relic)

		end_time = time.time()
		total_time = round(end_time - start_time, 2)
		print(' done after {}'.format(total_time))

	def load_reward_sell_prices(self, relic_tier, reset=True):
		if not self.prices_loaded:
			for rotation in self.rewards:
				for relic in self.rewards[rotation]:
					relic.get_average_price(ORDER_SELL, relic_tier)
		else:
			print('prices already loaded')
		self.prices_loaded = reset
		
	def get_price(self, rotation=MISSION_ROTATION_A, relic_tier=RELIC_TIER0, price_type=ORDER_SELL, debug=False):
		'''returns the average price of the selected rotation/relic tier/order type'''
		price = 0
		if not self.prices_loaded:
			self.load_reward_sell_prices(relic_tier)
		if rotation not in MISSION_ROTATIONS:
			raise ValueError('Rotation invalid')
		for relic in self.rewards[rotation]:
			price += relic.drop_chance / 100 * relic.sell_price[relic_tier]
		return round(price, 0)

	def load_all_prices(self):
		self.load_reward_sell_prices(RELIC_TIER0, reset=False)
		self.load_reward_sell_prices(RELIC_TIER1, reset=False)
		self.load_reward_sell_prices(RELIC_TIER2, reset=False)
		self.load_reward_sell_prices(RELIC_TIER3, reset=False)

	def parse(self):
		data = {}
		data['planet'] = self.planet
		data['name'] = self.name
		data['rewards'] = {}
		for rotation in self.rewards:
			data['rewards'][rotation] = []
			for relic in self.rewards[rotation]:
				parsed_reward = relic.parse()
				data['rewards'][rotation].append(parsed_reward)
		return data

	def save(self):
		self.load_all_prices()
		file_name = 'missions/{}-{}.json'.format(self.planet, self.name)
		with open(file_name, 'w') as file:
			data = self.parse()
			json.dump(data, file)
			print('saved {}'.format(file_name))
			