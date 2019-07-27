from wilib2 import *
import asyncio
import json
import aiohttp
import item

class Rotation():
	def __init__(self, rotation):
		self.type = rotation

	async def load_items(self, session):
		resp = await fetch_drop_data(session, )

