from pprint import pprint
import wilib2
import asyncio
import aiohttp
import numpy as np


wilib2.DUMP_MODE_ENABLED = True
class Item():
	def __init__(self, name, drop_chance=100):
		self.name = name
		self.drop_chance = drop_chance
		self.isForma = 'forma' in name.split('_') # checks whether item_name has 'Forma' in it


	async def load_sell_price(self, session):
		if self.isForma:
			self.sell_price = 0
		else:
			self.sell_price = await wilib2.fetch_order_sell_price(session, self.name)

	async def load_buy_price(self, session):
		if self.isForma:
			self.buy_price = 0
		else:
			self.buy_price = await wilib2.fetch_order_buy_price(session, self.name)

	async def load_average_price(self, session):
		await self.load_sell_price(session)

	def __repr__(self):
		return self.name




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

class Rotation():
	def __init__(self, _type, parent_mission = None, rewards = []):
		self.type = _type
		self.parent_mission = parent_mission
		self.rewards = rewards

	def set_rewards(self, rewards):
		self.rewards = rewards

	async def load_reward_prices(self, session):
		await asyncio.gather(*[asyncio.create_task(reward.load_average_price(session)) for reward in self.rewards])

	def get_average_price(self):
		pass

	def __repr__(self):
		return f'{self.type}'




class Mission():
	def __init__(self, planet_name, mission_name):
		self.name = mission_name
		self.planet = planet_name

	async def load_rewards(self, session):
		info = await wilib2.fetch_drop_data(session, f'missionRewards/{self.planet}/{self.name}.json')
		self.type = info['gameMode']
		rewards = info['rewards']
		self.has_rotations = len(info['rewards']) > 1
		self.rotations = []


		if self.has_rotations: # has rotations
			for rotation_pos, rotation in enumerate(rewards):
				rot = Rotation(rotation, self)
				r = []
				for reward in rewards[rotation]:

					# append a relic or item object to rewards 

					if 'Relic' in reward['itemName']:
						r.append(Relic(full_name = reward['itemName'], drop_chance = reward['chance']))
					elif not 'Endo' in reward['itemName']:
						name = wilib2._encode(reward['itemName'])
						r.append(Item(name, drop_chance = reward['chance']))
					else:
						# endo case - leave empty
						pass
				rot.set_rewards(r)
				self.rotations.append(rot)

		else:
			pass
	async def get_average_price(self, session):
		self.average_price = 0
		for rotation in self.rotations:
			await rotation.load_reward_prices(session)
			for reward in rotation.rewards:
				# print(reward.sell_price, reward.drop_chance)
				self.average_price += reward.sell_price * (100/reward.drop_chance)



		
	def get_rotations(self):
		return self.rotations

	def __repr__(self):
		return f'{self.planet} {self.mission}'

'''

TEST CODE 
async def main():
	async with aiohttp.ClientSession() as session:
		test_mission = Mission('Sedna','Hydron')
		await test_mission.load_rewards(session)
		await test_mission.get_average_price(session)


		#test_relic = Relic('Neo N3 Relic', relic_tier=wilib2._relic_tier3)
		#await test_relic.load_drops(session)
		#await test_relic.load_average_price(session)
		
		#print(test_relic.sell_price)


if __name__ == '__main__':
	wilib2.enable_dump_mode()
	asyncio.run(main())

	'''