import request
import aiohttp
import asyncio


async def main():
	async with aiohttp.ClientSession() as session:
		with open('list.txt') as file:
			names = [line.replace('\n', '').split(' ') for line in file]
			sum = 0
			for relic in names:
				average = await request.get_average_relic_price(session, relic[0], relic[1], tier='Radiant')
				sum += average * int(relic[2])
				print(f'{relic[0]} {relic[1]} : {average}')
			print(sum)





if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	request.enable_dump_mode()
	loop.run_until_complete(main())
	request.clear_dump()