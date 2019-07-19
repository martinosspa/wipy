from tkinter import *
import asyncio
import aiohttp
import wilib2
import threading
entries = []
_order_sell = 'sell'
_order_buy = 'buy'
_order_both = 'both'
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
			if self.order_type == _order_buy:
				item = await wilib2.fetch_order_sell_price(session, self.item_name)
			else:
				item = await wilib2.fetch_order_buy_price(session, self.item_name)
			self.price = item['price']
			self.text = f'{self.item_name} {self.order_type} price : {self.price}'
			self.label = Label(self.parent_window, text=self.text).grid(column=0, row=self.position)
			self.button = Button(self.parent_window, text='>', cursor='hand2', command=self.create_window).grid(column=1, row=self.position)
	def create_window(self):
		self.window = Toplevel(self.parent_window)
		self.window.title(self.item_name)
		msg = Message(self.window, text='aaaaaaaaaaaaaaaaaaaaaaaaaa')
		msg.pack()




def setup_basic_interface():
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
	order_mode.set(_order_sell)

	radiobutton_both = Radiobutton(window, text='Both', variable=order_mode, value=_order_both).grid(column=4, row=0)
	radiobutton_sell = Radiobutton(window, text='Sell', variable=order_mode, value=_order_sell).grid(column=5, row=0)
	radiobutton_buy = Radiobutton(window, text='Buy', variable=order_mode, value=_order_buy).grid(column=6, row=0)

def addLoop():
	loop = asyncio.new_event_loop()
	global order_mode
	item_name = textBox.get()
	textBox.delete(0, END)
	if order_mode.get() == 'both':
		entry1 = InterfaceEntry(window, item_name, _order_sell)
		entries.append(entry1)
		entry2 = InterfaceEntry(window, item_name, _order_buy)
		entries.append(entry2)
		loop.run_until_complete(entry1.fetch())
		loop.run_until_complete(entry2.fetch())
		
		
	else:
		entry = InterfaceEntry(window, item_name, order_mode.get())
		loop.run_until_complete(entry.fetch())
		entries.append(entry)

	loop.close()
	

def addNewEntry():
	thread = threading.Thread(target=addLoop)
	thread.start()

if __name__ == '__main__':
	setup_basic_interface()
	window.mainloop()


	# tigris_prime_set