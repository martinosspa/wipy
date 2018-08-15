from urllib.request import Request, urlopen
import json
from pprint import pprint
# 1. get location of a given relic
# 2. get BEST location for a given relic
# 3.
def get_data(url_extension):
	req = Request('http://drops.warframestat.us/data{}'.format(url_extension), headers={'User-Agent': 'Mozilla/5.0'})
	url_data = urlopen(req).read()
	return json.loads(url_data)

def get_all_data(request):
	return get_data('/all.json')

def encode(string):
	return string.lower().replace(' ', '_')

def decode(string):
	return string.title().replace('_', ' ')

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


def get_relic_drops(relic_era, relic_name):
	return get_data('/relics/{}/{}.json'.format(relic_era, relic_name))