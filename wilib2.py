from urllib.request import urlopen, Request
from pprint import pprint 
import json
import time
import numpy as np
import aiohttp
import asyncio
import threading
import os.path

_api_base_url = 'https://api.warframe.market/v1/items'
_drop_url = 'http://drops.warframestat.us'
global _relic_tier0
global _relic_tier1
global _relic_tier2
global _relic_tier3
_relic_tier0 = 'Intact'
_relic_tier1 = 'Exceptional'
_relic_tier2 = 'Flawless'
_relic_tier3 = 'Radiant'

request_counter = 0
DUMP_MODE_ENABLED = False

def enable_dump_mode():
	if not os.path.exists(f'dump'):
		os.mkdir('dump')
	DUMP_MODE_ENABLED = True

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

def _encode(str):
	splitted = str.split(' ')
	if len(splitted) == 4 and 'Blueprint' in splitted:
		# warframe blueprint, need to remove 'Blueprint' from str
		space = ' '
		splitted.remove('Blueprint')
		str = space.join(splitted)

	return str.lower().replace(' ', '_').replace('\'', '')

def filter_order(orders, _type='sell'):
	orders = list(map(_filter_order, orders))
	orders = list(filter(lambda order: order['order_type'] == _type , orders))
	orders = list(filter(lambda order: order['platform'] == 'pc', orders))
	orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))
	return orders
	#prices = list(map(lambda order: order['platinum'], orders))



async def fetch_drop_data(session, endpoint):
	async with session.get(f'{_drop_url}/data/{endpoint}') as resp:
		r = await resp.json()
		return r
	

# GETS MIN BUY PRICE
async def fetch_order_sell_price(session, item_name, additional_info=False):
	orders = (await fetch_orders(session, item_name))['orders']
	orders = filter_order(orders)

	prices = [order['platinum'] for order in orders]

	if len(prices) > 0:
		pos = np.argmin(prices)
		price = prices[pos]
		if additional_info:
			# returns price with addiotional info
			return {'price' : price,
				'customer' : {'name' : orders[pos]['user']['ingame_name'],
							  'region': orders[pos]['region']}}
		else:
			# just returns the price

			return price
	else:
		if additional_info:
			pos = None
			price = 0

			return {'price' : 0,
				'customer' : None }
		else:
			return 0


# GETS MAX SELL PRICE
async def fetch_order_buy_price(session, item_name, additional_info=False):
	orders = (await fetch_orders(session, item_name))['orders']
	orders = filter_order(orders, _type='buy')

	prices = [order['platinum'] for order in orders]
	if len(prices) > 0:
		pos = np.argmax(prices)
		price = prices[pos]
		name = orders[pos]['user']['ingame_name']
		region = orders[pos]['user']['region']

	else:
		pos = None
		price = 0

	if additional_info:
		return {'item_name' : item_name,
				'price' : price,
				'user_name' : name,
				'user_region': region}
	else:
		return price

async def fetch_info(session, item_name):
	async with session.get(f'{_api_base_url}/{item_name}') as response:
		json = await response.json()
		return json['payload']

async def fetch_stats(session, item_name):
	async with session.get(f'{_api_base_url}/{item_name}/statistics') as response:
		json = await response.json()
		return {'item_name' : item_name,
					'stats' : json['payload']}

async def fetch_orders(session, item_name):
	if DUMP_MODE_ENABLED:
		if os.path.exists(f'dump/{item_name}.json'):
			with open(f'dump/{item_name}.json', 'r') as f:
				info = json.load(f)
				return {'item_name' : item_name,
						'orders' : info}

	async with session.get(f'{_api_base_url}/{item_name}/orders') as response:
		resp = await response.json()
		if 'payload' in resp:
			if 'orders' in resp['payload']:
				global request_counter
				request_counter += 1
				if DUMP_MODE_ENABLED:
					with open(f'dump/{item_name}.json', 'w') as f:
						json.dump(resp['payload']['orders'], f)
				return {'item_name' : item_name,
						'orders' : resp['payload']['orders']}
			else:
				return None
		else:
			return None

async def fetch_all_buy_prices(session, item_names, additional_info=False):
	results = await asyncio.gather(*[asyncio.create_task(fetch_order_buy_price(session, item_name))
									for item_name in item_names])
	return results

async def fetch_all_sell_prices(session, item_names, additional_info=False):
	results = await asyncio.gather(*[asyncio.create_task(fetch_order_sell_price(session, item_name, additional_info=additional_info))
									for item_name in item_names])
	return results

async def fetch_all_orders(session, item_names, additional_info=False):
	results = await asyncio.gather(*[asyncio.create_task(fetch_orders(session, item_name))
									for item_name in item_names])
	return results

async def fetch_all_stats(session, item_names):
	results = await asyncio.gather(*[asyncio.create_task(fetch_stats(session, item_name))
									for item_name in item_names])
	return results

async def fetch_all_info(session, item_names):
	results = await asyncio.gather(*[asyncio.create_task(fetch_info(session, item_name))
									for item_name in item_names])
	return results


async def get_average_relic_price(session, era, name, tier=_relic_tier0):
	resp = await fetch_drop_data(session, f'relics/{era}/{name}.json')
	resp = resp['rewards'][tier]
	
	resp = list(filter(lambda item: not item['itemName'] == 'Forma Blueprint', resp))
	item_names = [_encode(item['itemName']) for item in resp]
	chances = [item['chance'] for item in resp]
	l = await fetch_all_sell_prices(session, item_names, additional_info=True)
	prices = [item['price'] for item in l]
	return sum(np.multiply(prices, chances)) / 100

async def load_missions(session, planet_name):
	resp = await fetch_drop_data(session, 'missionRewards.json')
	return resp['missionRewards'][planet_name]


async def main():

	# test area - relic
	async with aiohttp.ClientSession() as session:
		test = await get_average_relic_price(session,'Neo', 'R2')
		print(test)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())