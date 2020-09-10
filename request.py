from urllib.request import urlopen, Request
from pprint import pprint 
import json
import time
import numpy as np
import aiohttp
import asyncio
import threading
import shutil
import os
#shutil.rmtree('/folder_name')

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


_request_counter = 0
DUMP_MODE_ENABLED = False
def enable_dump_mode():
	if not os.path.exists(f'dump'):
		os.mkdir('dump')
	global DUMP_MODE_ENABLED
	DUMP_MODE_ENABLED = True

def clear_dump():
	global DUMP_MODE_ENABLED
	if DUMP_MODE_ENABLED:
		shutil.rmtree('dump', ignore_errors=True)


def _filter_orders(orders, _type='sell'):
	orders = list(filter(lambda order: order['order_type'] == _type , orders))
	orders = list(filter(lambda order: order['platform'] == 'pc', orders))
	orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))
	orders = list(map(_filter_order, orders))
	return orders

def _encode(str):
	splitted = str.split(' ')
	if len(splitted) == 4 and 'Blueprint' in splitted:
		#print(str)
		if not str == 'Nami Skyla Prime Blueprint':
			# warframe blueprint, need to remove 'Blueprint' from str
			space = ' '
			splitted.remove('Blueprint')
			str = space.join(splitted)

	return str.lower().replace(' ', '_').replace('\'', '').replace('&', 'and')
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

async def fetch_drop_data(session, endpoint):
	async with session.get(f'{_drop_url}/data/{endpoint}') as resp:
		r = await resp.json()
		return r


async def fetch_orders(session, item_name):
	'''Fetches order based on item name'''

	#If dump mode is enabled instead of requesting from API it gets it from the file
	if os.path.exists(f'dump/{item_name}.json'):
		with open(f'dump/{item_name}.json', 'r') as f:
			info = json.load(f)
			return info
	else:
		async with session.get(f'{_api_base_url}/{item_name}/orders') as response:
			resp = await response.json()
			if 'error' in resp:
				raise Exception(f'Wrong Item Name {item_name}')
			# item is valid
			global _request_counter
			_request_counter += 1
			global DUMP_MODE_ENABLED
			if DUMP_MODE_ENABLED:
				print('ad')
				with open(f'dump/{item_name}.json', 'w') as f:
					json.dump(resp['payload']['orders'], f)
			return resp['payload']['orders']

				

async def get_sell_price(session, item_name, additional_info=False):
	'''Gets maximum sell price'''
	orders = await fetch_orders(session, item_name)
	orders = _filter_orders(orders, _type='buy')
	prices = [order['platinum'] for order in orders]
	if len(prices) > 0:
		# check whether the list is empty
		pos = np.argmax(prices)
		if additional_info:
			# returns price with addiotional info
			return {'price' : prices[pos],
				'customer' : {'name' : orders[pos]['user']['ingame_name'],
							  'region': orders[pos]['region']}}
		else:
			return prices[pos]
	else:
		# list was empty
		if additional_info:
			return {'price' : None, 'customer' : None}
		# list was empty
		return 0

async def get_buy_price(session, item_name, additional_info=False):
	'''Gets minimum buy price'''
	orders = await fetch_orders(session, item_name)
	orders = _filter_orders(orders, _type='sell')
	prices = [order['platinum'] for order in orders]

	if len(prices) > 0:
		# check whether the list is empty
		pos = np.argmin(prices)
		if additional_info:
			# returns price with addiotional info
			return {'price' : prices[pos],
				'customer' : {'name' : orders[pos]['user']['ingame_name'],
							  'region': orders[pos]['region']}}
		else:
			return prices[pos]
	else:
		# list was empty
		if additional_info:
			return {'price' : None, 'customer' : None}
		# list was empty
		return 0

	print(orders)

async def get_all_sell_prices(session, item_names, additional_info=False):
	results = await asyncio.gather(*[asyncio.create_task(get_sell_price(session, item_name, additional_info=additional_info))
									for item_name in item_names])
	return results

async def get_average_relic_price(session, era, name, tier=_relic_tier0):
	resp = await fetch_drop_data(session, f'relics/{era}/{name}.json')
	resp = resp['rewards'][tier]
	
	resp = list(filter(lambda item: not item['itemName'] == 'Forma Blueprint', resp))
	item_names = [_encode(item['itemName']) for item in resp]
	chances = [item['chance'] for item in resp]
	prices = await get_all_sell_prices(session, item_names)
	#prices = [item['price']  for item in l]
	#print(prices)
	return sum(np.multiply(prices, chances)) / 100



async def main():
	async with aiohttp.ClientSession() as session:
		enable_dump_mode()
		average = await get_average_relic_price(session, 'Meso', 'G1', tier=_relic_tier0)
		average2 = await get_average_relic_price(session, 'Meso', 'G1', tier=_relic_tier0)
		average3 = await get_average_relic_price(session, 'Meso', 'G1', tier=_relic_tier0)
		clear_dump()
		print(average)
		print(_request_counter)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())











