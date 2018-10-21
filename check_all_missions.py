import wilib1_5 as wilib
from pprint import pprint
import json
all_missions = []
errors = 0
for planet in wilib.star_chart:
	for mission in wilib.star_chart[planet]:
		try:
			all_missions.append(wilib.Mission(planet, mission, wilib.RELIC_TIER0))
		except KeyError:
			errors += 1
			pass
		else:
			pass
best_mission = ''
best_price = 0
best_rotation = ''
all_prices = {}

print('getting prices')
for mission in all_missions:
	mission.load_average_price()
	#rotation = mission.rotations[0]
	mission_all_rotations_average = 0
	for rotation in mission.rotations:
		mission_all_rotations_average += 0.25 * rotation.average_price

	all_prices[mission.name] = mission_all_rotations_average

	if mission_all_rotations_average > best_price:
		best_mission = mission.name
		best_planet = mission.planet
		best_price = mission_all_rotations_average
		#best_rotation = rotation.type


sorted_prices = sorted(all_prices, key=all_prices.get)
for mission in sorted_prices:
	mission = all_prices[mission]
with open('all_prices.json', 'w') as f:
	json.dump(sorted_prices, f)
print(f'best mission: {best_planet}-{best_mission} for {best_price} platinum on rotation {best_rotation}')

print(f'errors: {errors}')
print(f'{wilib.requests} requests to warframe.market API')
