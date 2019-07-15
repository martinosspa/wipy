import numpy as np
from urllib.request import urlopen, Request
import json
from pprint import pprint
import sys

warframe_market_url = 'https://api.warframe.market/v1/items'

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


def get_both_item(item_name):
	req = Request(f'{warframe_market_url}/{item_name}/orders')
	orders = json.loads(urlopen(req).read())['payload']['orders']
	#filter orders
	orders = list(filter(lambda order: order['platform'] == 'pc', orders))
	orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))

	sell_orders = list(filter(lambda order: order['order_type'] == 'sell', orders))
	buy_orders = list(filter(lambda order: order['order_type'] == 'buy', orders))

	sell_prices = list(map(lambda order: order['platinum'], sell_orders))
	buy_prices = list(map(lambda order: order['platinum'], buy_orders))

	if len(sell_prices) > 1:
		sell_position = np.argmax(sell_prices)
		sell_price = sell_prices[sell_position]
		seller = sell_orders[sell_position]['user']['ingame_name']
	else:
		sell_price = 0
		seller = None

	if len(buy_prices) > 1:
		buy_position = np.argmin(buy_prices)
		buy_price = buy_prices[buy_position]
		buyer = buy_orders[buy_position]['user']['ingame_name']
	else:
		buy_price = 0
		buyer = None

	return {'sell_price'  : sell_price,
			'seller_name' : seller,
			'buy_price' : buy_price,
			'buyer_name'  : buyer}


def get_item(item_name):
	req = Request(f'{warframe_market_url}/{item_name}/orders')


	orders = json.loads(urlopen(req).read())['payload']['orders']

	#filter orders
	
	orders = list(filter(lambda order: order['order_type'] == 'buy', orders))
	orders = list(filter(lambda order: order['platform'] == 'pc', orders))
	orders = list(filter(lambda order: order['user']['status'] == 'ingame', orders))

	prices = list(map(lambda order: order['platinum'], orders))
	max_price = prices[np.argmax(prices)]
	sellers = []
	for order in orders:
		if order['platinum'] == max_price:
			sellers.append(order['user']['ingame_name'])
	print(f'Buy price: {max_price} platinum from {sellers}')





def get_all_items():
	req = Request(f'{warframe_market_url}')
	all_items = json.loads(urlopen(req).read())['payload']['items']['en']

	for item in all_items:
		info = get_both_item(item['url_name'])
		if info['sell_price'] < info['buy_price']:
			p = info['buy_price'] - info['sell_price']
			sn = info['seller_name']
			bn = info['buyer_name']
			name = item['item_name']
			print(f'{name} for {p} | {sn} > {bn}')

if __name__ == "__main__":
	if len(sys.argv) == 2:
		get_item(sys.argv[1])
	else:
		get_all_items()