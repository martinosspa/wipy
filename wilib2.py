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




# GETS MIN BUY PRICE
async def fetch_order_sell_price(session, item_name):
	orders = (await fetch_orders(session, item_name))['orders']

	#t = threading.Thread(target=filter_order, argBNBs=orders)
	#t.start()
	orders = filter_order(orders)

	prices = list(map(lambda x: x['platinum'], orders))
	pos = np.argmin(prices)
	price = prices[pos]
	#pprint(orders)
	return {'item_name' : item_name,
			'price' : price}


# GETS MAX SELL PRICE
async def fetch_order_buy_price(session, item_name):
	orders = (await fetch_orders(session, item_name))['orders']

	#t = threading.Thread(target=filter_order, args=orders)
	#t.start()
	orders = filter_order(orders, _type='buy')

	prices = list(map(lambda order: order['platinum'], orders))
	pos = np.argmax(prices)
	price = prices[pos]
	#pprint(orders)
	return {'item_name' : item_name,
			'price' : price}


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

async def main():
	async with aiohttp.ClientSession() as session:
		# get all items and parse them into url names
		#resp = await session.get(f'{_api_base_url}')
		#all_items = await resp.json()
		#all_items = all_items['payload']['items']['en']
		#items = [item['url_name'] for item in all_items]
		items = ['tigris_prime_set']

		htmls = await fetch_all_orders(session, items)
		for item in htmls:
			print(item['item_name'])
			
			#with open('all-items-json/{}.json'.format(item['item_name']), 'w+') as f:
				#json.dump(item, f)

if __name__ == '__main__':
	asyncio.run(main())