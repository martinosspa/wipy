from urllib.request import urlopen, Request
from pprint import pprint 
import json
import time
import numpy as np
import aiohttp
import asyncio
import threading

_api_base_url = 'https://api.warframe.market/v1/items'
_drop_url = 'http://drops.warframestat.us'

_relic_tier0 = 0
_relic_tier1 = 1
_relic_tier2 = 2
_relic_tier3 = 3




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
async def fetch_order_sell_price(session, item_name):
	orders = (await fetch_orders(session, item_name))['orders']

	#t = threading.Thread(target=filter_order, argBNBs=orders)
	#t.start()
	orders = filter_order(orders)

	prices = list(map(lambda x: x['platinum'], orders))
	if len(prices) > 0:
		pos = np.argmin(prices)
		price = prices[pos]
		return {'price' : price,
			'customer' : {'name' : orders[pos]['user']['ingame_name'],
						  'region': orders[pos]['region']}}
	else:
		pos = None
		price = 0
		return {'price' : 0,
			'customer' : None }


# GETS MAX SELL PRICE
async def fetch_order_buy_price(session, item_name):
	orders = (await fetch_orders(session, item_name))['orders']

	#t = threading.Thread(target=filter_order, args=orders)
	#t.start()
	orders = filter_order(orders, _type='buy')

	prices = list(map(lambda order: order['platinum'], orders))
	pos = np.argmax(prices)
	price = prices[pos]
	name = orders[pos]['user']['ingame_name']
	region = orders[pos]['user']['region']
	#pprint(orders)
	return {'item_name' : item_name,
			'price' : price,
			'user_name' : name,
			'user_region': region}

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
	async with session.get(f'{_api_base_url}/{item_name}/orders') as response:
		json = await response.json()
		if 'orders' in json['payload']:
			return {'item_name' : item_name,
					'orders' : json['payload']['orders']}
		else:
			return None

async def fetch_all_buy_prices(session, item_names):
	results = await asyncio.gather(*[asyncio.create_task(fetch_order_buy_price(session, item_name))
									for item_name in item_names])
	return results

async def fetch_all_sell_prices(session, item_names):
	results = await asyncio.gather(*[asyncio.create_task(fetch_order_sell_price(session, item_name))
									for item_name in item_names])
	return results

async def fetch_all_orders(session, item_names):
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

async def main():
	async with aiohttp.ClientSession() as session:
		# get all items and parse them into url names
		#resp = await session.get(f'{_api_base_url}')
		#all_items = await resp.json()
		#all_items = all_items['payload']['items']['en']
		#items = [item['url_name'] for item in all_items]
		test_item = ['tigris_prime_set']

		htmls = await fetch_all_orders(session, test_item)
		for item in htmls:
			print(item['item_name'])
			
			#with open('all-items-json/{}.json'.format(item['item_name']), 'w+') as f:
				#json.dump(item, f)

if __name__ == '__main__':
	asyncio.run(main())