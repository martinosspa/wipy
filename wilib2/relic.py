from wilib2 import *
import asyncio
import json
import aiohttp
from wilib2 import _relic_tier0

class Relic():
	def __init__(self, name, tier = _relic_tier0):
		self.era, self.name, _ = name.split(' ')
		self.tier = tier
		
	def __init__(self, era, name, tier = _relic_tier0):
		self.name = name
		self.era = era
		self.tier = tier

	async def get_average_price(self, session):
		self.average_price = await get_average_relic_price(session, self.era, self.name, tier = self.tier)



