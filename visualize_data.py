from urllib.request import Request, urlopen
import json
from pprint import pprint
import matplotlib.pyplot as plt

def main():
	req = Request('http://api.warframe.market/v1/items/tigris_prime_set/statistics')
	data = json.loads(urlopen(req).read())['payload']['statistics_closed']['48hours']
	pprint(data[0])
	dates = list(map(lambda point: point['datetime'], data))
	median = list(map(lambda point: point['median'], data))
	average = list(map(lambda point: point['avg_price'], data))
	print(len(data))
	plt.plot(dates, median)
	plt.plot(dates, average)
	plt.show()


if __name__ == '__main__':
	main()