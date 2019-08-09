from wilib2 import *

import asyncio
import json
import aiohttp
import item
from relic import *

class Rotation():
	def __init__(self, parent_planet, mission, rotation):
		self.type = rotation
		self.planet = parent_planet
		self.mission = mission

	async def load_items(self, session):
		resp = await fetch_drop_data(session, f'missionRewards/{self.planet}/{self.mission}.json')
		#asyncio.run(self.load_item_prices(session))
		self.r = resp['rewards'][self.type]

	async def load_item_prices(self, session):
		self.rewards = []
		pprint(self.r)
		for item in self.r:
			if 'Relic' in item['itemName']:
				self.rewards.append(Relic(item['itemName']))


		await asyncio.gather(*[asyncio.create_task(session, item)
								for item in self.rewards])


async def main():

	# testing the module
	async with aiohttp.ClientSession() as session:
		test = Rotation('Sedna', 'Hydron', 'A')
		await test.load_items(session)
		await test.load_item_prices(session)
		pprint(test.rewards)


if __name__ == '__main__':
	asyncio.run(main())
