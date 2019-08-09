from wilib2 import *
import asyncio
import json
import aiohttp
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
			rot = Rotation(rotation)
			self.rotations.append(rot)





async def main():
	''' test mission'''
	m = Mission('Hydron', 'Sedna')
	async with aiohttp.ClientSession() as session:
		await m.load_rotations(session)
		for rot in m.rotations:
			print(rot.type)
		#print(m)

if __name__ == '__main__':
	asyncio.run(main())
