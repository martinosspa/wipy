import wilib2
from pprint import pprint
import json
import aiohttp
import asyncio

async def main():
	async with aiohttp.ClientSession() as session:
		all_missions

if __name__ == '__main__':
	asyncio.run(main())