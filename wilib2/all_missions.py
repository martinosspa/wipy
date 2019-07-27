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

def _filter_name(name):
	return name.lower().replace(' ', '_').replace('-', '_').replace('\'', '')

def _filter_planet_missions(planet_name):
	# filters the missions of a planet if game mode is not desired
	for mission in dict(planet_name):
		if planet_name[mission]['gameMode'] not in interested_game_modes:
			planet_name.pop(mission)

def add_to_interested_items(planet_name):
	# adds all items that are not credits and endo to a list
	for mission in all_planets[planet_name]:
		for rotation in all_planets[planet_name][mission]['rewards']:
			for reward in all_planets[planet_name][mission]['rewards'][rotation]:
				if reward['itemName'] not in interested_items:
					interested_items.append(reward['itemName'])

def process_planet(planet_name):
	# filter unwanted reward	
	for mission in all_planets[planet_name]:
		for rotation in all_planets[planet_name][mission]['rewards']:
			rewards = all_planets[planet_name][mission]['rewards'][rotation]
			rewards = list(filter(lambda r: not not_intrested_rewards[0] in r['itemName'], rewards))
			rewards = list(filter(lambda r: not not_intrested_rewards[1] in r['itemName'], rewards))
			
			all_planets[planet_name][mission]['rewards'][rotation] = rewards


def dump_planet(planet_name):
	# dump planet data as a json
	with open(f'all-items-json/{planet_name}.json', 'w') as f:
		json.dump(all_planets[planet_name], f)




async def get_items():
	global interested_items
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
			pool.map(process_planet, all_planets)
			pool.map(add_to_interested_items, all_planets)
			print(len(interested_items)) 

		relics = []
		for item in interested_items:
			if 'Relic' in item:
				relics.append(item)
		for r in relics:
			interested_items.remove(r)
		interested_items = list(map(_filter_name, interested_items))
		interested_items.remove('mutalist_alad_v_nav_coordinate')
		interested_items.remove('forma_blueprint')
		interested_items.remove('octavia_neuroptics_blueprint')
		results = await wilib2.fetch_all_sell_prices(session, interested_items)


if __name__ == '__main__':
	asyncio.run((get_items()))