from wilib2 import *
import asyncio
import json
import aiohttp
from pprint import pprint
from item import *
from rotation import *
from planet import *
class Mission():
	def __init__(self, parent_planet, mission_name):
		if type(parent_planet) is not str:
			# constructed from a parent data, can grab all data from that planet object
			info = parent_planet._missions[mission_name]
			self.name = mission_name
			self.planet_name = parent_planet.name
			self.rotations = info['rewards']
			self.type = info['gameMode']
			pprint(self.rotations)
		else:
			self.name = mission_name
			self.planet_name = parent_planet



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
