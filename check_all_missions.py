import wilib1_1 as wilib
from pprint import pprint

#pp1 = wilib.PrimePart('soma_prime_barrel')
#pp1.load_price()


#r1 = wilib.Relic('Axi', 'A1')
#r1.load_price()
#pprint(r1._parse())

all_missions = []
errors = 0
for planet in wilib.star_chart:
	for mission in wilib.star_chart[planet]:
		try:
			all_missions.append(wilib.Mission(planet, mission))
		except KeyError:
			errors += 1
			pass
		else:
			pass
best_mission = ''
best_price = 0
best_rotation = ''

print('getting prices')
for mission in all_missions:
	mission.load_average_price()
	for rotation in mission.rotations:
		if rotation.average_price > best_price:
			best_mission = mission.name
			best_price = rotation.average_price
			best_rotation = rotation.type
	#mission.save()
print(f'best mission: {best_mission} for {best_price} platinum on rotation {best_rotation}')

#m1 = wilib.Mission('sedna', 'hydron')
#m1.load_average_price()
#m1.save()
print(f'errors: {errors}')
print(f'{wilib.requests} requests to warframe.market API')
