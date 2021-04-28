from urllib.request import urlopen, Request
from pprint import pprint
import json
import aiohttp
import asyncio
import threading

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
_optimization = False





async def _fetch_orders(session, item_name, additional_info=False):
	if _optimization:
		# TODO
		pass

	async with session.get(f'{_api_base_url}/{item_name}/orders') as response:
		json_data = await response.json()
		if additional_info:
			return {'item_name' : item_name,
					'orders' : json_data['payload']['orders']}
		else:
			return json_data['payload']['orders']




async def get_sell_max_price(session, item_name, additional_info=False):
	# note : item_name must be encoded
	fetched_orders = await _fetch_orders(session, item_name)

	# manual search for the highest price
	max_price_order_info = None
	max_price = 0
	for order in fetched_orders:
		if order['platinum'] > max_price and order['order_type'] == 'buy':
			max_price = order['platinum']
			max_price_order_info = order
	if additional_info:
		# TODO
		wanted_info = {}
		wanted_info['platform'] = order['platform']
	else:
		return {'price' : order['platinum'],
				'username' : order['user']['ingame_name'],
				'region' : order['user']['region']}








async def main():
	async with aiohttp.ClientSession() as session:
		test = await get_sell_max_price(session, 'tigris_prime_set')
		pprint(test)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
