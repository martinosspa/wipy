from tkinter import *
import asyncio
import aiohttp
import wilib2
from functools import partial
import time
import threading

entries = []
BG_COLOR = '#202020'
WG_COLOR = '#3f4042'
FR_COLOR = '#1A1A1A'
ACTIVE_COLOR = '#313131'

def refresh_counter():
	# attaches event loop to the thread
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	print('second thread running')
	while True:
		loop.run_until_complete(refresh())
		time.sleep(60)

async def refresh():
	global entries
	print('refreshing..')
	await asyncio.gather(*[asyncio.create_task(entry.fetch()) for entry in entries])

def add_entry(item_name, order_type):
	global window
	global entries
	global add_window
	# in case 'both' is selected
	if order_type == 3:
		entries.append(InterfaceEntry(window, item_name, 1))
		entries.append(InterfaceEntry(window, item_name, 2))
	else:
		entries.append(InterfaceEntry(window, item_name, order_type))
	add_window.destroy()

class InterfaceEntry():
	def __init__(self, parent_window, item_name, order_type):
		self.text = ''
		self.item_name = item_name.replace(' ', '_').lower()
		self.display_name = item_name.capitalize()
		self.position = len(entries)+1
		self.price = None
		self.order_type = order_type
		self.parent_window = parent_window
		self.prev_price = 0
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.fetch())

	async def fetch(self):
		async with aiohttp.ClientSession() as session:
			if self.order_type == 1:
				self.info = await wilib2.fetch_order_sell_price(session, self.item_name, additional_info=True)
			else:
				self.info = await wilib2.fetch_order_buy_price(session, self.item_name, additional_info=True)

			self.price = self.info['price']

			# label for the said item with price 

			self.text = f'{self.display_name} {self.order_type} price : {self.price}'
			self.label = Label(self.parent_window, text=self.text)
			self.label.grid(column=0, row=self.position)
			self.label.config(bg=WG_COLOR)

			'''
	def create_window(self):
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._create_window())
		loop.stop()
		loop.close()
	async def _create_window(self):

		self.window = Toplevel()
		self.window.geometry('200x200')
		self.window.title(self.item_name)
		user_name = self.info['user_name']
		user_region = self.info['user_region']
		msg = Message(self.window, text=f'{user_name}[{user_region}]')
		msg.pack()
		'''



# global function that sets up the basic window
def main():
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

	global order_mode
	order_mode = StringVar(master=window)
	order_mode.set('1')

	# THREAD HANDLING
	global entry_thread
	entry_thread = threading.Thread(target=refresh_counter)
	entry_thread.setDaemon(True)
	entry_thread.start()
	window.mainloop()


def newEntryWindow():
	global add_window
	add_window = Toplevel()
	add_window.geometry('400x200')
	add_window.title('Add new order to track')
	add_window.configure(bg=BG_COLOR)
	
	lbl = Label(add_window, text="Enter item to track:", bg=BG_COLOR, fg='#FFFFFF', anchor='w').grid(column=0, row=0)

	search_box = Entry(add_window)
	
	search_box.grid(column=1, row=0)
	global _order_mode
	_order_mode = IntVar()
	
	Radiobutton(add_window, activebackground=ACTIVE_COLOR, bg=BG_COLOR, text="Sell", variable=_order_mode, value=1).grid(column=0,row=1)
	Radiobutton(add_window, activebackground=ACTIVE_COLOR, bg=BG_COLOR, text="Buy", variable=_order_mode, value=2).grid(column=1,row=1)
	Radiobutton(add_window, activebackground=ACTIVE_COLOR, bg=BG_COLOR, text="Both", variable=_order_mode, value=3).grid(column=2,row=1)


	# TODO: FIX POSITION OF SEARCH BUTTON
	global entry_thread
	search_button = Button(add_window, text='Search', command=lambda: add_entry(search_box.get(), _order_mode.get()), fg='#FFFFFF', bg=WG_COLOR).grid(column=2, row=0)



if __name__ == '__main__':
	main()



	# tigris_prime_set