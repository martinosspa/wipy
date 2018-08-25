from urllib.request import Request, urlopen
import json
import riw
from pprint import pprint
import time

def encode(string):
	for item in riw.all_items:
		if item['item_name'] == string:
			return item['url_name']
	return string.lower().replace(' ', '_').replace('&', 'and').replace('_blueprint', '')
		
def decode(string):
	return string.title().replace('_', ' ').replace('and', '&')

class Mission:
	def __init__(self, planet_name, mission_name):
		self.name = mission_name
		self.planet_name = planet_name

		self.mission_type = ''
		self.rewards = []
		print('{} {} loaded')
	def load(self):
		self.data = get_data('/missionRewards/{}/{}.json'.format(self.planet_name.capitalize(), self.name.capitalize()))
		self.rotations = self.data['rewards']
		self.mission_type = self.data['gameMode'].lower()
		self.has_rotations = type(self.rotations) == dict
		self.rewards = []
		if self.has_rotations:
			for rotation in self.rotations:
				for reward in self.rotations[rotation]:
					self.split_name = reward['itemName'].split(' ') 
					if 'Relic' in self.split_name:
						self.rewards.append(Relic(self.split_name[0], self.split_name[1], reward['chance']))
						
		else:
			for reward in self.rotations:
				self.split_name = reward['itemName'].split(' ')
				if 'Relic' in self.split_name:
					self.rewards.append(Relic(self.split_name[0], self.split_name[1], reward['chance']))
	def get_prices(self):
		for relic in self.rewards:
			relic.get_price()
	def save(self):
		self.all_json_data = {'name': self.name,
							  'mission_type': self.mission_type,
							  'has_rotations': self.has_rotations,
							  'rewards': {}}
		with open('{}_{}.json'.format(self.planet_name, self.name), 'w') as file:
			json.dump(self.all_json_data, file)

	def load_prices(self):
		for reward in self.rewards:
			reward.get_price

class Mod:
	def __init__(self, name):
		self.url_name = encode(name)
		self.normal_name = decode(name)
		self.price = 0

	def get_price(self, order_type):
		self.price = riw.request_mod(self.url_name, order_type, 0)['price']
	

class Blueprint:
	def __init__(self, name):
		self.url_name = encode(name)
		self.normal_name = decode(name)
		self.price = 0
	def get_price(self, order_type):
		self.price = riw.request_item(self.url_name, order_type)



class Relic:
	def __init__(self, relic_era, relic_name, chance):
		self.era = relic_era
		self.name = relic_name
		self.info = {}
		self.data = get_data('/relics/{}/{}.json'.format(self.era, self.name), verbose=False)
		#pprint(self.data)
		
		for refinement in self.data['rewards']:
			self.info[refinement.lower()] = []
			for reward in self.data['rewards'][refinement]:
				self.start_time = time.time()
				if not reward['itemName'].encode() == 'forma':
					self.info[refinement.lower()].append(Blueprint(reward['itemName']))
				self.end_time = time.time()
				#print(reward['itemName'], self.end_time - self.start_time)
		self.drop_chance = chance
		

	def get_price(self, verbose=False):
		
		for refinement in self.info:
			for reward in self.info[refinement]:
				#print(reward.url_name)
				reward.get_price('sell')



def get_data(url_extension, verbose=False):
	start = time.time()
	url = 'http://drops.warframestat.us/data{}'.format(url_extension)
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_data = urlopen(req).read()
	end = time.time()
	if verbose:
		print('{} took {:0.2f} seconds'.format(url, end - start))
	return json.loads(url_data)

def get_all_data(request):
	return get_data('/all.json')





def get_relic_drops(relic_era, relic_name):
	return get_data('/relics/{}/{}.json'.format(relic_era, relic_name))

def get_item_relic(item_name):
	relics = []
	data = get_data('/relics.json')
	for relic in data['relics']:
		for reward in relic['rewards']:
			relic_info = {
					'relic_name': relic['relicName'],
					'relic_era' : relic['tier']
					}
			if reward['itemName'] == item_name and not relic_info in relics:
				relics.append(relic_info)
	return relics

hydron = Mission('sedna', 'hydron')
hydron.load()

hydron.get_prices()
