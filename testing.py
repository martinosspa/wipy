import rid
import riw
from pprint import pprint
import math
forbidden_items = ['forma_blueprint']

all_items = riw.request_all_items()
data = rid.get_data('/missionRewards.json')['missionRewards']
for planet in data:
	for mission in data[planet]:
		#print(data[planet][mission]['gameMode'])
		#print(len(data[planet][mission]['rewards']))
		for rotation in data[planet][mission]['rewards']:
			if type(data[planet][mission]['rewards']) == dict:
				for rotation_reward in data[planet][mission]['rewards'][rotation]:
					#print(rotation_reward)
					relic = {'name': rotation_reward['itemName'],
							'drop_chance': rotation_reward['chance']}
					split_name = relic['name'].split(' ')
					
					if 'Relic' in split_name:
						drops = rid.get_relic_drops(split_name[0], split_name[1])
						
						
						relic_average_price = 0
						for relic_reward in drops['rewards']['Intact']:
							encoded_name = rid.encode(relic_reward['itemName'])
							encoded_name = encoded_name.replace('&', 'and')
							if not riw.item_exists(encoded_name) and not encoded_name in forbidden_items:
								encoded_name = encoded_name.replace('_blueprint', '')
							if encoded_name not in forbidden_items:
								info = riw.request_item(encoded_name, 'buy')
								if not info['isEmpty']:
									relic_average_price += math.ceil(relic_reward['chance']) / 100 * info['price']
						print(relic['name'], relic_average_price)