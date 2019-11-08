import wilib2
from pprint import pprint
import json
import aiohttp
import asyncio


drop_url = 'http://drops.warframestat.us'
mission_points = {'Arena': 2,
					'Assassination': 3,
					'Assault': 3, 
					'Capture': 5,
					'Defection': 5,
					'Defense': 10,
					'Survival': 10,
					'Disruption': 4,
					'Excavation': 10,
					'Exterminate': 6,
					'Free Roam': 7,
					'Bounty': 7,
					'Hijack': 5,
					'Infested Salvage': 4,
					'Interception': 8,
					'Junction': 3,
					'Mobile Defense': 5,
					'Pursuit': 1,
					'Rescue': 7,
					'Rush': 1,
					'Sabotage': 4,
					'Sanctuary Onslaught': 8,
					'Spy': 7,
					'Caches': 4,
					'Conclave': 1
					}




async def main():
	async with aiohttp.ClientSession() as session:	
		resp = await session.get(f'{drop_url}/data/all.json')
		ALL_DATA = await resp.json()
		planets = ALL_DATA['missionRewards']

		for planet in planets:
			p = {'name': planet
				 'missions': {}}
			for mission_name in planets[planet]:
				mission = planets[planet][mission_name]
				p['missions'][mission_name] = {'rotations': []}

				#gamemode_points = mission_points[mission['gameMode']]
				for _rotation in mission['rewards']:
					p['missions'][mission_name] = 
					rotation = mission['rewards'][_rotation]
					

					for reward in rotation:
						reward_name = rotation[reward]['itemName']
						reward_chance = rotation[reward]['chance']
			




	'''
	async with aiohttp.ClientSession() as session:
		resp = await session.get(drop_url + '/data/relics.json')
		relics = await resp.json()
		relics = relics['relics']
		resp = await session.get(drop_url + '/data/missionRewards.json')
		mission_rewards = await resp.json()
		mission_rewards = mission_rewards['missionRewards']

		for planet in mission_rewards:
			for mission in mission_rewards[planet]:
				m = mission_rewards[planet][mission]
				gamemode_points = mission_points[m['gameMode']]

				for rotation in m['rewards']:
					rewards = []
					if type(m['rewards']) == dict:
						rotation_rewards = m['rewards'][rotation]
						pprint(rotation_rewards)
						'''



if __name__ == '__main__':
	asyncio.run(main())