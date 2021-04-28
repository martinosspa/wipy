from wilib2 import *
import asyncio
import json
import aiohttp

class Relic():
	def __init__(self, full_name=None, era=None, name=None, relic_tier=wilib2._relic_tier0, drop_chance=100):
		if full_name:
			self.era, self.name, _ = full_name.split(' ')
		else:
			self.era = era
			self.name = name
		self.tier = relic_tier
		self.drop_chance = drop_chance
		self.rewards = []


	async def load_drops(self, session):
		#loads drops
		drops = (await wilib2.fetch_drop_data(session , f'relics/{self.era}/{self.name}.json'))['rewards'][self.tier]
		self.rewards = []
		for item in drops:
			encoded_item_name = wilib2._encode(item['itemName'])
			self.rewards.append(Item(encoded_item_name, drop_chance=item['chance']))

	async def load_average_price(self, session):
		# in case rewards were not loaded

		if not self.rewards:
			await self.load_drops(session)
		rewards = self.rewards.copy()
		items = [item.name for item in rewards]

		# dont want to check forma's price
		if 'forma_blueprint' in items:
			items.remove('forma_blueprint')

		# loads sell prices
		await asyncio.gather(*[asyncio.create_task(item.load_sell_price(session)) for item in self.rewards])
		
		# calculates average per relic open
		prices = [item.sell_price for item in self.rewards]
		chances = [item.drop_chance/100 for item in self.rewards]
		#print(prices)
		#print(chances)
		self.sell_price = sum(np.multiply(prices, chances))


	def __repr__(self):
		return f'{self.era} {self.name} [{self.tier}] '