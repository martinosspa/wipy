from wilib2 import *
import asyncio
import json
import aiohttp

class Item():
	def __init__(self, item_name):
		self.name = item_name


	async def get_sell_price(self, session):
		resp = await fetch_order_sell_price(session, self.name)
		self.price = resp['price']
		self.customer = resp['customer']['name']
		self.region = resp['customer']['region']

	def _parse(self):
		r = {}
		r['name'] = self.name
		r['price'] = self.price
		r['customer'] = f'{self.customer}[{self.region}]'
		return r


async def main():
	''' test item'''
	item = Item('tigris_prime_set')
	async with aiohttp.ClientSession() as session:
		await item.get_sell_price(session)
		print(item.price)

if __name__ == '__main__':
	asyncio.run(main())



