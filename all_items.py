import wilib2
import aiohttp
import asyncio

async def main():
	async with aiohttp.ClientSession() as session:
		resp = await session.get(f'{wilib2._api_base_url}')
		all_items = await resp.json()
		#print(all_items)
		all_items = all_items['payload']['items']
		items = [item['url_name'] for item in all_items]
		htmls = await wilib2.fetch_all_orders(session, items)
		for html in htmls:
			print(html['item_name'])
			#print(html)

if __name__ == '__main__':
	asyncio.run((main()))