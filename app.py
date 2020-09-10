from tkinter import *
import asyncio
import aiohttp
import wilib2
from functools import partial

import threading

entries = []
_order_sell = 'sell'
_order_buy = 'buy'
_order_both = 'both'
BG_COLOR = '#202020'
WG_COLOR = '#3f4042'
FR_COLOR = '#1A1A1A'
#entry_thread = EntryThread(1, 'Entry-Thread')
class EntryThread():
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.id = threadID
		self.name = name
		self.entries = []

	# this will be run by an internal counter to refresh all entries
	def run(self):
		pass




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
				self.info = await wilib2.fetch_order_sell_price(session, self.item_name, additional_info=True)
			else:
				self.info = await wilib2.fetch_order_buy_price(session, self.item_name, additional_info=True)

			self.price = self.info['price']

			# label for the said item with price 
			self.text = f'{self.item_name} {self.order_type} price : {self.price}'
			self.label = Label(self.parent_window, text=self.text)
			self.label.grid(column=0, row=self.position)
			self.label.config(bg=WG_COLOR)

			# open new window button
			self.button = Button(self.parent_window, text='>', cursor='hand2', command=self.create_window)
			self.button.grid(column=1, row=self.position)
			self.button.config(bg=WG_COLOR)


	def create_window(self):
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._create_window())
	async def _create_window(self):

		self.window = Toplevel()
		self.window.geometry('200x200')
		self.window.title(self.item_name)
		user_name = self.info['user_name']
		user_region = self.info['user_region']
		msg = Message(self.window, text=f'{user_name}[{user_region}]')
		msg.pack()



# global function that sets up the basic window
def setup_basic_interface():

	# main window setup
	global window
	window = Tk()
	window.title('Warframe Market Tracker')
	window.geometry('600x800')
	window.configure(bg=BG_COLOR)

	# upper frame
	upper_frame = Frame(window, bg=FR_COLOR, width=600, height=25).grid(column=0, row=0,columnspan=9)

	# add order button
	button_add = Button(upper_frame, text='Add', command=newEntryWindow, bg=WG_COLOR).grid(column=0, row=0, sticky='W')


	#lbl = Label(window, text="Enter Item Id:", bg=BG_COLOR).grid(column=0, row=4)
	global textBox
	#textBox = Entry(window, width=20)
	#textBox.grid(column=1, row=4)
	#
	


	global order_mode
	order_mode = StringVar(master=window)
	order_mode.set(_order_sell)

	#Radiobutton(window, text='Both', variable=order_mode, value=_order_both, bg=WG_COLOR).grid(column=4, row=4)
	#Radiobutton(window, text='Sell', variable=order_mode, value=_order_sell, bg=WG_COLOR).grid(column=5, row=4)
	#Radiobutton(window, text='Buy', variable=order_mode, value=_order_buy, bg=WG_COLOR).grid(column=6, row=4)


def add_entry(item_name, order_type):
	global entry_thread
	entry_thread.add_entry(item_name, order_type)

def start_search(item_name):
	loop = asyncio.new_event_loop()
	loop.run_until_complete(addEntry(item_name))

def newEntryWindow():
	add_window = Toplevel()
	add_window.geometry('400x200')
	add_window.title('Add new order to track')
	add_window.configure(bg=BG_COLOR)
	
	lbl = Label(add_window, text="Enter item to track:", bg=BG_COLOR, foreground='#FFFFFF', anchor='w').grid(column=0, row=0)

	search_box = Entry(add_window)
	
	search_box.grid(column=1, row=0)

	# TODO: FIX POSITION OF SEARCH BUTTON
	search_button = Button(add_window, text='Search', command=lambda: add_entry(search_box.get()), foreground='#FFFFFF', bg=WG_COLOR).grid(column=2, row=0)
	




	'''
	global order_mode
	item_name = textBox.get()
	textBox.delete(0, END)
	if order_mode.get() == 'both':
		entry1 = InterfaceEntry(window, item_name, _order_sell)
		entries.append(entry1)
		entry2 = InterfaceEntry(window, item_name, _order_buy)
		entries.append(entry2)

		# NOTE: can be updated to asynchronous
		loop.run_until_complete(entry1.fetch())
		loop.run_until_complete(entry2.fetch())
		
		
	else:
		entry = InterfaceEntry(window, item_name, order_mode.get())
		loop.run_until_complete(entry.fetch())
		entries.append(entry)
	'''
	#loop.close()


if __name__ == '__main__':
	setup_basic_interface()
	window.mainloop()


	# tigris_prime_set