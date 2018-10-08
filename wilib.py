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
	for planet in all_data:
		for mission in all_data[planet]:
			missions.append(Mission(planet, mission))
	return missions

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

		req = Request('{}/{}/orders'.format(warframe_market_api_base_url, self.url_name))
		orders = json.loads(urlopen(req).read())['payload']['orders']
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


		# get relic drop rewards from the api
		start_time = time.time()
		raw_data = get_drop_data('/relics/{}/{}.json'.format(self.era.capitalize(),
																  self.url_name.capitalize()),
																  verbose=verbose)
		data = raw_data['rewards']
		for tier in data:
			self.rewards[tier] = []
			for reward in data[tier]:
				split_name = reward['itemName'].lower().split(' ')
				if 'forma' in split_name:
					self.rewards[tier].append(Forma(reward['chance']))
				else:
					self.rewards[tier].append(PrimePart(reward['itemName'], reward['chance']))
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
		return average_price

	def parse(self):
		'''returns the relic object into json format'''
		rewards = {}
		for tier in self.rewards:
			rewards[tier] = []
			for reward in self.rewards[tier]:
				rewards[tier].append({'name': reward.name,
								'url_name': reward.url_name,
								'drop_chance': reward.drop_chance})
		data = {'name': self.name,
				'era': self.era,
				'url_name': self.url_name,
				'relic_tiers': rewards}
		return data

class Mission:
	def __init__(self, mission_planet, mission_name, debug=False):
		# basic object variables

		self.planet = mission_planet.capitalize()
		self.name = mission_name.capitalize()
		self.total_sell_price = 0
		self.game_mode = None
		self.has_rotations = False
		print('initalizing {} {}'.format(self.planet.lower(), self.name.lower()))
		start_time = time.time()

		# loads rewards from all rotations
		data = get_drop_data('/missionRewards/{}/{}.json'.format(self.planet.capitalize(),
																 self.name.capitalize())
																)
		self.game_mode = data['gameMode']

		# filters out non-relic rewards
		filtered_rewards = {}
		for rotation in data['rewards']:
			filtered_rewards[rotation] = list(filter(lambda relic: 'Relic' in relic['itemName'].split(' '), data['rewards'][rotation]))
		
		# initiates a relic object dictionary
		self.rewards = {}
		for rotation in filtered_rewards:
			self.rewards[rotation] = []
			for relic in filtered_rewards[rotation]:
				split_name = relic['itemName'].split(' ')
				relic_era = split_name[0]
				relic_name = split_name[1]
				relic = Relic(relic_era, relic_name, relic['chance'])
				self.rewards[rotation].append(relic)
		end_time = time.time()
		total_time = round(end_time - start_time, 2)
		print(' done after {}'.format(total_time))


	def get_price(self, rotation=MISSION_ROTATION_A, relic_tier=RELIC_TIER0, price_type=ORDER_SELL, debug=False):
		'''returns the average price of the selected rotation/relic tier/order type'''
		price = 0
		if rotation not in MISSION_ROTATIONS:
			raise ValueError('Rotation invalid')
		for relic in self.rewards[rotation]:
			relic_price = relic.get_average_price(price_type, relic_tier, debug=debug)
			price += relic.drop_chance / 100 * relic_price
		return round(price, 0)

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
		with open('{}-{}.json'.format(self.planet, self.name), 'w') as file:
			data = self.parse()
			json.dump(data, file)