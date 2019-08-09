from wilib2 import *
import asyncio
import json
import aiohttp
from pprint import pprint
from item import *
from rotation import *
class Mission():
	def __init__(self, mission_name, parent_planet_name):
		self.name = mission_name
		self.planet_name = parent_planet_name

	async def load_rotations(self, session):
		resp = await fetch_drop_data(session, f'missionRewards/{self.planet_name}/{self.name}.json')
		#self.drop_data = resp['rewards']
		self.rotations = []
		for rotation in resp['rewards']:
			rot = Rotation(self.planet_name, self.name, rotation)

			self.rotations.append(rot)
		for rot in self.rotations:
			await rot.load_items(session)





async def main():
	''' test mission'''
	m = Mission('Hydron', 'Sedna')
	async with aiohttp.ClientSession() as session:
		await m.load_rotations(session)
		pprint(m.rotations[0].rewards)
		#for rot in m.rotations:
		#	pprint(rot.rewards)
		#print(m)

if __name__ == '__main__':
	asyncio.run(main())
