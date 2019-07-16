from tkinter import *
import asyncio
import aiohttp
import wilib2
import threading
entries = []
_order_sell = 'sell'
_order_buy = 'buy'
class InterfaceEntry():
	def __init__(self, parent_window, item_name, order_type):
		self.text = ''
		self.item_name = item_name
		self.position = len(entries)+1
		self.price = None
		self.order_type = order_type
		self.parent_window = parent_window


	async def fetch(self):
		async with aiohttp.ClientSession() as session:
			print(self.item_name)
			if self.order_type == _order_buy:
				item = await wilib2.fetch_order_sell_price(session, self.item_name)
			else:
				item = await wilib2.fetch_order_buy_price(session, self.item_name)

			self.price = item['price']
			self.text = f'{self.item_name} {self.order_type} price : {self.price}'
			self.label = Label(self.parent_window, text=self.text).grid(column=0, row=self.position)




def setup_interface():
	global window
	window = Tk()
	window.title('Warframe Market Tracker')
	window.geometry('600x450')


	lbl = Label(window, text="Enter Item Id:").grid(column=0, row=0)
	global textBox
	textBox = Entry(window, width=20)
	textBox.grid(column=1, row=0)
	btn = Button(window, text='Add', command=addNewEntry).grid(column=3, row=0)


	global order_mode
	order_mode = StringVar(master=window)
	order_mode.set('both')

	radiobutton_both = Radiobutton(window, text='Both', variable=order_mode, value='both').grid(column=4, row=0)
	radiobutton_sell = Radiobutton(window, text='Sell', variable=order_mode, value='sell').grid(column=5, row=0)
	radiobutton_buy = Radiobutton(window, text='Buy', variable=order_mode, value='buy').grid(column=6, row=0)

'''
async def addEntry():
	async with aiohttp.ClientSession() as session:
		entry = entries[-1]
		item = None
		if entry[1] == 'sell':
			item = await wilib2.fetch_order_buy_price(session, entry[0])
		elif entry[1] == 'buy':
			item = await wilib2.fetch_order_sell_price(session, entry[0])
		elif entry[1] == 'both':
			item_sell = await wilib2.fetch_order_buy_price(session, entry[0])
			item_buy = await wilib2.fetch_order_sell_price(session, entry[0])

		if item or not entry[1] == 'both': # in case order_mode isnt set
			price = item['price']
			item_name = item['item_name']
			text = f'{item_name} {order_mode.get()} price : {price}'
			l = Label(window, text=text).grid(column=0, row=len(entries)+1)

		elif entry[1] == 'both':
			price = item_sell['price']
			item_name = item_sell['item_name']
			text = f'{item_name} sell price : {price}'
			l1 = Label(window, text=text).grid(column=0, row=len(entries)+1)


			price = item_buy['price']
			item_name = item_buy['item_name']
			text = f'{item_name} buy price : {price}'
			l2 = Label(window, text=text).grid(column=0, row=len(entries)+2)

			entries.append((entries[-1][0], 'buy'))
			entries[-2] = (entries[-1][0], 'sell')
'''


'''
async def updateDisplay():
	async with aiohttp.ClientSession() as session:
		# 1 = sell, 2 = buy
		htmls = None
		if order_mode.get() == 'sell':
			htmls = await wilib2.fetch_all_buy_prices(session, entries)
		elif order_mode.get() == 'buy':
			htmls = await wilib2.fetch_all_sell_prices(session, entries)
		if htmls:
			start = 0
			for item in htmls:
				start += 1
				#average = item['stats']['statistics_live']['48hours'][-1]['avg_price']
				price = item['price']
				name = item['item_name']

				t = f'{name} {order_mode.get()} price: {price}'
				text = Label(window, text=t)
				text.grid(column=0, row=start)
'''
def addLoop():
	loop = asyncio.new_event_loop()
	global order_mode
	if order_mode.get() == 'both':

	else:
		entry = InterfaceEntry(window, textBox.get(), order_mode.get())
	ss = loop.run_until_complete(entry.fetch())
	entries.append(entry)
	loop.close()
	textBox.delete(0, END)

def addNewEntry():
	s = threading.Thread(target=addLoop)
	s.start()



if __name__ == '__main__':
	setup_interface()
	window.mainloop()


	# tigris_prime_set