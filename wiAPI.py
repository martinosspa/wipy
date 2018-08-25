from urllib.request import urlopen, Request
from pprint import pprint
import json
import time
import numpy as np
warframe_market_api_base_url = 'https://api.warframe.market/v1/items'
warframe_drop_data_url = 'http://drops.warframestat.us/data'
ERA_LITH = 'lith'
ERA_MESO = 'meso'
ERA_NEO = 'neo'
ERA_AXI = 'axi'
FORMA = 'forma'
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
	def __init__(self):
		Reward.__init__(self, FORMA)
		self.name = FORMA
		self.price = 10
		self.customer = None

class PrimePart(Reward):
	def __init__(self, part_name):
		Reward.__init__(self, part_name)
		
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

		#filter orders
		self.orders = list(map(_filter, self.orders))
		self.orders = list(filter(lambda order: order['order_type'] == order_type.lower(), self.orders))
		self.orders = list(filter(lambda order: order['platform'] == 'pc', self.orders))
		self.orders = list(filter(lambda order: order['user']['status'] == 'ingame', self.orders))
		self.prices = list(map(lambda order: order['platinum'], self.orders))
		self.customer_info = list(map(lambda order: {order['user']['ingame_name'], 
													 order['user']['region']}, self.orders ))
		#print(self.orders)
		self.position = np.argmin(self.prices) if order_type == ORDER_SELL else np.argmax(self.prices)
		self.position = 0
		self.price = self.prices[self.position]
		self.customer = self.customer_info[self.position]
		self.end_time = time.time()
		if verbose:
			print('{} took {} seconds'.format(self.url_name, self.end_time - self.start_time))



class Relic:
	def __init__(self, relic_era, relic_name, verbose=False):
		if not relic_era in ERAS:
			raise ValueError('not a valid relic era')
		self.era = relic_era
		self.name = encode(relic_name)
		self.url_name = decode(relic_name)
	def load_rewards(self, verbose=False):
		self.start_time = time.time()
		self.raw_data = get_drop_data('/relics/{}/{}.json'.format(self.era.capitalize(),
																  self.url_name.capitalize()),
																  verbose=verbose)

		self.rewards = []
		for reward in self.raw_data['rewards']['Intact']:
			self.split_name = reward['itemName'].lower().split(' ')
			if 'forma' in self.split_name:
				self.rewards.append(Forma())
			else:
				self.rewards.append(PrimePart(reward['itemName']))
		self.end_time = time.time()
		if verbose:
			print('{} took {} seconds'.format(self.url_name, self.end_time - self.start_time))

r = Relic(ERA_AXI, 'r1')
r.load_rewards(verbose=False)
#print(r.rewards)
for reward in r.rewards:
	reward.get_price(ORDER_SELL)
	#print(reward.price)
	