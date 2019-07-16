import wilib2
import aiohttp
import asyncio
import json
from pprint import pprint
import itertools
from multiprocessing.dummy import Pool as ThreadPool 

_mission_endpoint = 'data/missionRewards.json'
interested_game_modes = ['Defense', 'Interception', 'Survival']
not_intrested_rewards = ['Credits', 'Endo']
interested_items = []
def _filter_planet_missions(planet):
	# filters the missions of a planet if game mode is not desired
	for mission in dict(planet):
		if planet[mission]['gameMode'] not in interested_game_modes:
			planet.pop(mission)



def process_planet(planet):
	# filter unwanted reward	
	planets_copy = dict(all_planets)

	for mission in all_planets[planet]:
		for rotation in all_planets[planet][mission]['rewards']:
			_rotation = all_planets[planet][mission]['rewards'][rotation]
			rewards = list(filter(lambda r: not_intrested_rewards[0] in r['itemName'], _rotation))
			rewards = list(filter(lambda r: not_intrested_rewards[1] in r['itemName'], _rotation))
	#with open(f'all-items-json/{planet}.json', 'w') as f:
	#	json.dump(all_planets[planet], f)	





async def main():
	async with aiohttp.ClientSession() as session:
		resp2 = await session.get(f'{wilib2._drop_url}/{_mission_endpoint}')
		global all_planets
		all_planets = await resp2.json()
		all_planets = all_planets['missionRewards']
		all_planets.pop('Sanctuary')
		# filters missions by gamemode
		for planet in all_planets:
			_filter_planet_missions(all_planets[planet])

		with ThreadPool(8) as pool:
			results = pool.map(process_planet, all_planets)
			#zip(itertools.repeat(constant), list_a)
		#with open('test.json', 'w') as f:
		#	json.dump(all_planets, f)

if __name__ == '__main__':
	asyncio.run((main()))