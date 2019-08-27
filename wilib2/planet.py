from wilib2 import *
import asyncio
import aiohttp
import json
from mission import *

class Planet():
	def __init__(self, name):
		self.name = name
		self.missions = []

	def __eq__(self, other):
		return self.name == other.name


	async def load_missions(self, session):
		self._missions = await load_missions(session, self.name)
		for mission in self._missions:
			self.missions.append(Mission(self, mission))




async def main():
	planet = Planet('Sedna')
	async with aiohttp.ClientSession() as session:
		await planet.load_missions(session)
		
if __name__ == '__main__':
	asyncio.run(main())