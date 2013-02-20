#!/usr/bin/env python2
import pygtk
pygtk.require("2.0")
import gtk, gobject
import httplib, sqlite3, os, sys, datetime
from threading import Thread
from bs4 import BeautifulSoup

class creeper:
	def __init__(self):
		"""
		Layout:
		+ VBox2 --------------------------------------------------+
		|  + MenuBar1 -------------------------------------------+|
		|  + HBox1 ----------------------------------------------+|
		|  | label1 | ComicID | SearchBtn                        ||
		|  +-----------------------------------------------------+|
		|  + NoteBook1-------------------------------------------+|
		|  |  + VBox1 ------------------------------------------+||
		|  |  |  + frame2 +                                     |||
		|  |  |  | label2 |                                     |||
		|  |  |  +--------+                                     |||
		|  |  |  + frame1 -----------+                          |||
		|  |  |  |  + table1 ------+ |                          |||
		|  |  |  |  | Button | ... | |                          |||
		|  |  |  |  +--------+-----+ |                          |||
		|  |  |  |  |  ...   | ... | |                          |||
		|  |  |  |  +--------------+ |                          |||
		|  |  |  +-------------------+                          |||
		|  |  +-------------------------------------------------+||
		|  +-----------------------------------------------------+|
		|  + FSpeparator ----------------------------------------+|
		|  + HBox2 ----------------------------------------------+|
		|  | ProgressBar | StatusBar                             ||
		|  +-----------------------------------------------------+|
		+---------------------------------------------------------+
		"""
		self.window = gtk.Window()
		self.window.set_title("Comic Creeper")
		self.window.set_size_request(700, 450)
		self.window.connect("delete_event", self.delete)
		gtk.gdk.threads_init()
		
		# Default Configuration
		self.config = {}
		self.config['FileDir'] = os.path.realpath(os.path.dirname(sys.argv[0]))
		self.config['IconDir'] = self.config['FileDir'] + '/icon'
		self.config['DownloadDir'] = self.config['FileDir'] + '/Download'

		self.InitDB()
		
		# Load configuration from db
		for i in self.ExecuteDB('SELECT * FROM config'):
			self.config[i[0]] = i[1]
		
		# StatusBar
		self.StatusBar = gtk.Statusbar()
		self.StatusBar.push(0, "Ready")
		self.StatusBar.show()
		
		# Label
		self.label1 = gtk.Label("Comic ID")
		self.label1.set_justify(gtk.JUSTIFY_CENTER)
		self.label1.set_line_wrap(True)
		self.label1.show()

		# Frame for showing comic index
		self.frame1 = gtk.Frame("Index")
		self.frame1.show()

		# Frame for showing comic info
		self.frame2 = gtk.Frame('Info')
		self.frame2.show()

		# Text entry
		self.ComicID = gtk.Entry(5)
		self.ComicID.connect('key_press_event', self.CommitComicID)
		self.ComicID.show()

		# Button for handling input ID
		self.SearchBtn = gtk.Button("Commit", gtk.STOCK_OK)
		self.SearchBtn.connect("clicked", self.Search, self.ComicID)
		self.SearchBtn.show()

		# Foot Separator
		self.FSpeparator = gtk.HSeparator()
		self.FSpeparator.show()
		
		# Menu Widget
		## Menu Items
		self.InfoItem = gtk.MenuItem("About")
		self.InfoItem.connect('activate', self.ShowAboutInfo)
		self.InfoItem.show()
		self.AboutItem = gtk.MenuItem("About")
		self.AboutItem.show()
		## Menu ( Container )
		self.Menu1 = gtk.Menu()
		self.Menu1.show()
		## Menu Bar
		self.MenuBar1 = gtk.MenuBar();
		self.MenuBar1.show()
		## Packing
		self.Menu1.append(self.InfoItem)
		self.AboutItem.set_submenu(self.Menu1)
		self.MenuBar1.append(self.AboutItem)
		
		# NoteBook Widget
		self.NoteBook1 = gtk.Notebook()
		self.NoteBook1.popup_enable()
		self.NoteBook1.set_scrollable(True)
		self.NoteBook1.show()
		
		# Progress Bar
		self.ProgressBar = gtk.ProgressBar()
		self.ProgressBar.show()
		
		# Create download manager tab page
		## Create TreeStore : (comic id, comic name, time, progress)
		self.DMTreeStore = gtk.TreeStore(str, str, str, float)
		## Create TreeViewColumn
		self.DMTreeViewCol1 = gtk.TreeViewColumn('Name')
		self.DMTreeViewCol2 = gtk.TreeViewColumn('Time')
		self.DMTreeViewCol3 = gtk.TreeViewColumn('Progress')
		self.DMTreeViewCol1.set_resizable(True)
		self.DMTreeViewCol2.set_resizable(True)
		self.DMTreeViewCol3.set_resizable(True)
		## Create Cell Renderer
		self.DMCell1 = gtk.CellRendererText()
		self.DMCell2 = gtk.CellRendererText()
		self.DMCell3 = gtk.CellRendererProgress()
		## Create Tree View
		self.DMTreeView = gtk.TreeView(self.DMTreeStore)
		self.DMTreeView.append_column(self.DMTreeViewCol1)
		self.DMTreeView.append_column(self.DMTreeViewCol2)
		self.DMTreeView.append_column(self.DMTreeViewCol3)
		## Create Scroll Window
		TmpScrollWin = gtk.ScrolledWindow()
		TmpScrollWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		TmpScrollWin.set_vadjustment(self.DMTreeView.get_vadjustment())
		TmpScrollWin.add(self.DMTreeView)
		## Packing
		self.HBox4 = gtk.HBox(False)
		self.VBox4 = gtk.VBox(False)
		self.DMTreeViewCol1.pack_start(self.DMCell1, True)
		self.DMTreeViewCol2.pack_start(self.DMCell2, True)
		self.DMTreeViewCol3.pack_start(self.DMCell3, True)
		self.DMTreeViewCol1.add_attribute(self.DMCell1, 'text', 1)
		self.DMTreeViewCol2.add_attribute(self.DMCell2, 'text', 2)
		self.DMTreeViewCol3.add_attribute(self.DMCell3, 'value', 3)
		self.HBox4.pack_start(TmpScrollWin)
		self.HBox4.pack_start(self.VBox4, False, False, 10)
		self.NoteBook1.append_page(self.HBox4, 
				self.NewTabLabel('Download', self.HBox4, self.ToggleTab, self.HBox4, True))

		# Create bookmark manager tab page
		## Create TreeStore
		self.BMTreeStore = gtk.TreeStore(str, str)
		## Create TreeViewColumn
		self.BMTreeViewCol1 = gtk.TreeViewColumn('Name')
		self.BMTreeViewCol2 = gtk.TreeViewColumn('ID')
		self.BMTreeViewCol1.set_resizable(True)
		self.BMTreeViewCol2.set_resizable(True)
		## Create Tree View
		self.BMTreeView = gtk.TreeView(self.BMTreeStore)
		self.BMTreeView.connect('row-activated', self.TreeViewClickRow)
		self.BMTreeView.append_column(self.BMTreeViewCol1)
		self.BMTreeView.append_column(self.BMTreeViewCol2)
		## Create Cell Renderer
		self.BMCell1 = gtk.CellRendererText()
		self.BMCell2 = gtk.CellRendererText()
		## Create delete button
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU)
		button = gtk.Button()
		button.add(icon)
		button.connect('clicked', self.BMTreeViewDel)
		button.set_tooltip_text('Delete the bookmark')
		## Create Scroll Window
		TmpScrollWin = gtk.ScrolledWindow()
		TmpScrollWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		TmpScrollWin.set_vadjustment(self.BMTreeView.get_vadjustment())
		TmpScrollWin.add(self.BMTreeView)
		## Load db to show
		for data in self.ExecuteDB('SELECT * FROM bookmark'):
			self.BMTreeStore.append(None, data)
		## Packing
		self.HBox3 = gtk.HBox(False)
		self.VBox3 = gtk.VBox(False)
		self.VBox3.pack_start(button, False, False, 2)
		self.BMTreeViewCol1.pack_start(self.BMCell1, True)
		self.BMTreeViewCol2.pack_start(self.BMCell2, True)
		self.BMTreeViewCol1.add_attribute(self.BMCell1, 'text', 1)
		self.BMTreeViewCol2.add_attribute(self.BMCell2, 'text', 0)
		self.HBox3.pack_start(TmpScrollWin)
		self.HBox3.pack_start(self.VBox3, False, False, 10)
		self.NoteBook1.append_page(self.HBox3, 
				self.NewTabLabel('Bookmark', self.HBox3, self.ToggleTab, self.HBox3, True))

		# Create history manager tab page
		## Create TreeStore : (ComicID, Name, Time)
		self.HMTreeStore = gtk.TreeStore(str, str, str)
		## Create TreeViewColumn
		self.HMTreeViewCol1 = gtk.TreeViewColumn('Name')
		self.HMTreeViewCol2 = gtk.TreeViewColumn('ID')
		self.HMTreeViewCol3 = gtk.TreeViewColumn('Time')
		self.HMTreeViewCol1.set_resizable(True)
		self.HMTreeViewCol2.set_resizable(True)
		self.HMTreeViewCol3.set_resizable(True)
		## Create Tree View
		self.HMTreeView = gtk.TreeView(self.HMTreeStore)
		self.HMTreeView.connect('row-activated', self.TreeViewClickRow)
		self.HMTreeView.append_column(self.HMTreeViewCol1)
		self.HMTreeView.append_column(self.HMTreeViewCol2)
		self.HMTreeView.append_column(self.HMTreeViewCol3)
		## Create Cell Renderer
		self.HMCell1 = gtk.CellRendererText()
		self.HMCell2 = gtk.CellRendererText()
		self.HMCell3 = gtk.CellRendererText()
		## Create delete button
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU)
		button1 = gtk.Button()
		button1.add(icon)
		button1.connect('clicked', self.HMTreeViewDel)
		button1.set_tooltip_text('Delete the history')
		## Create delete_all button
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU)
		button2 = gtk.Button()
		button2.add(icon)
		button2.connect('clicked', self.HMTreeViewDelAll)
		button2.set_tooltip_text('Delete all the history')
		## Create Scroll Window
		TmpScrollWin = gtk.ScrolledWindow()
		TmpScrollWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		TmpScrollWin.set_vadjustment(self.HMTreeView.get_vadjustment())
		TmpScrollWin.add(self.HMTreeView)
		## Load db to show
		for data in self.ExecuteDB('SELECT * FROM history'):
			self.HMTreeStore.append(None, data)
		## Packing
		self.HBox5 = gtk.HBox(False)
		self.VBox5 = gtk.VBox(False)
		self.VBox5.pack_start(button1, False, False, 2)
		self.VBox5.pack_start(button2, False, False, 2)
		self.HMTreeViewCol1.pack_start(self.HMCell1, True)
		self.HMTreeViewCol2.pack_start(self.HMCell2, True)
		self.HMTreeViewCol3.pack_start(self.HMCell3, True)
		self.HMTreeViewCol1.add_attribute(self.HMCell1, 'text', 1)
		self.HMTreeViewCol2.add_attribute(self.HMCell2, 'text', 0)
		self.HMTreeViewCol3.add_attribute(self.HMCell3, 'text', 2)
		self.HBox5.pack_start(TmpScrollWin)
		self.HBox5.pack_start(self.VBox5, False, False, 10)
		self.NoteBook1.append_page(self.HBox5, 
				self.NewTabLabel('History', self.HBox5, self.ToggleTab, self.HBox5, True))
		
		# Create Config manager tab
		label1 = gtk.Label('Download Directory:')
		entry1 = gtk.Entry()
		entry1.set_text(self.config['DownloadDir'])
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
		button1 = gtk.Button()
		button1.add(icon)
		button1.connect('clicked', self.SelectDownloadDir, entry1)
		save_button = gtk.Button('Save', gtk.STOCK_SAVE)
		save_button.connect('clicked', self.SaveConfig, 'DownloadDir', entry1)
		## Packing
		self.HBox6 = gtk.HBox()
		self.VBox6 = gtk.VBox()
		self.HBox6.pack_start(label1, False, True)
		self.HBox6.pack_start(entry1, True, True)
		self.HBox6.pack_start(button1, False, False)
		self.VBox6.pack_start(self.HBox6, False, True)
		self.VBox6.pack_end(save_button, False, True)
		self.NoteBook1.append_page(self.VBox6, 
				self.NewTabLabel('Config', self.VBox6, self.ToggleTab, self.VBox6, True))
		
		# Tool Bar
		self.ToolBar = gtk.Toolbar()
		self.ToolBar.set_style(gtk.TOOLBAR_ICONS)
		self.ToolBar.set_tooltips(True)
		## Download icon
		icon = gtk.Image()
		icon.set_from_file( self.config['FileDir'] + '/icon/download.png')
		self.ToolBar.append_item('download', 'Download Manager', 'download', icon,
				self.ToggleTab, self.HBox4 )
		## Bookmark icon
		icon = gtk.Image()
		icon.set_from_file( self.config['IconDir'] +  '/bookmark.png')
		self.ToolBar.append_item('bookmark', 'Bookmark Manager', 'bookmark', icon,
				self.ToggleTab, self.HBox3 )
		## Config icon
		icon = gtk.Image()
		icon.set_from_file( self.config['IconDir'] +  '/config.png')
		self.ToolBar.append_item('config', 'Config Manager', 'config', icon,
				self.ToggleTab, self.VBox6 )
		## History icon
		icon = gtk.Image()
		icon.set_from_file( self.config['IconDir'] +  '/history.png')
		self.ToolBar.append_item('history', 'History Manager', 'history', icon,
				self.ToggleTab, self.HBox5 )
		self.ToolBar.show()
		
		# Packing
		self.VBox1 = gtk.VBox(False, 0)
		self.VBox2 = gtk.VBox(False, 0)
		self.HBox1 = gtk.HBox(True, 5)
		self.HBox2 = gtk.HBox(True, 0)
		## HBox1
		self.HBox1.pack_start(self.label1, False, True, 0)
		self.HBox1.pack_start(self.ComicID, True, True, 0)
		self.HBox1.pack_start(self.SearchBtn, False, True, 0)
		self.HBox1.show()
		self.VBox1.pack_start(self.frame2, True, True, 0)
		self.VBox1.pack_start(self.frame1, True, True, 0)
		self.VBox1.hide()
		self.NoteBook1.append_page(self.VBox1, gtk.Label('main'))
		self.VBox2.pack_start(self.MenuBar1, False, True, 0)
		self.VBox2.pack_start(self.ToolBar, False, True, 0)
		self.VBox2.pack_start(self.HBox1, False, True, 0)
		self.VBox2.pack_start(self.NoteBook1, True, True, 0)
		self.VBox2.pack_start(self.FSpeparator, False, True, 0)
		## HBox2
		self.HBox2.pack_start(self.ProgressBar, False, True, 0)
		self.HBox2.pack_start(self.StatusBar, False, True, 0)
		self.HBox2.show()
		self.VBox2.pack_start(self.HBox2, False, True, 0)
		self.VBox2.show()
		self.window.add(self.VBox2)
		self.window.show()
	
	def main(self):
		gtk.main()
	
	def delete(self, widget, event):
		self.Sqlcon.close()
		gtk.main_quit()
		return False

	def Search(self, widget, cid):
		"""
		cid for Comic ID, a text entry.
		"""
		t = Thread(target=self.ShowIndex, args=(cid.get_text(),))
		t.daemon = True
		t.start()
	
	def ShowIndex(self, cid):
		"""
		Create a new page and put the widget into it.
		cid for Comic ID, a string.
		"""
		self.StatusBar.push(0, 'Loading')
		url = 'www.8comic.com'
		
		# Checking input data if a numbe
		if cid.isdigit() == False :
			self.StatusBar.push(0, "Please input a Comic ID!")
			return
		
		# Frame for showing comic info
		TmpFrame2 = gtk.Frame('Info')
		TmpFrame2.show()
		
		# Init ProgressBar
		self.ProgressBar.set_fraction(0)
		
		src = self.GetWebData(url, '/html/' + cid + '.html')
		self.StepProgressBar(self.ProgressBar, 0.2)
		#gobject.idle_add(self.StepProgressBar, (self.ProgressBar, 0.2))
		if src == None :
			return
		# Get the index
		index = self.GetComicIndex(src)
		self.StepProgressBar(self.ProgressBar, 0.05)
		# Get the images code
		imgcode = self.GetImgCode(cid)
		self.StepProgressBar(self.ProgressBar, 0.2)
		## Packing index buttons with table
		row = len(index) // 5
		row += 1 if ((len(index) % 5) != 0) else 0
		TmpTable = gtk.Table(1, 1, True)
		num = len(index)
		k = 0
		for i in range(0, row):
			for j in range(0, 5 if num > 5 else num):
				btn = gtk.Button(index[k])
				btn.connect('clicked', self.ShowImgPage_thread, imgcode[k], index[k])
				k += 1
				TmpTable.attach(btn, j, j+1, i, i+1)
				btn.show()
			num -= 5
		TmpTable.show()
		
		# Get Comic Info
		info = self.GetComicInfo(src)
		tmps = ''
		tmps = '%s\n%s:\t%s' % (tmps, 'Name', info['Name'])
		tmps = '%s\n%s:\t%s' % (tmps, 'Intro', info['Intro'])
		TmpLabel = gtk.Label(tmps)
		TmpLabel.set_line_wrap(True)
		TmpLabel.connect('size-allocate', 
				lambda label, allocation: label.set_size_request(allocation.width - 20 , -1))
		TmpLabel.show()
		del tmps
		self.StepProgressBar(self.ProgressBar, 0.05)
		## log
		self.LogHistory(cid, info['Name'])
		## Get Comic Cover
		cover = gtk.Image()
		rawimg = self.GetWebData('www.8comic.com', '/pics/0/' + cid + 's.jpg', False)
		loader = gtk.gdk.PixbufLoader()
		loader.write(rawimg)
		loader.close()
		cover.set_from_pixbuf(loader.get_pixbuf())
		cover.show()
		self.StepProgressBar(self.ProgressBar, 0.2)
		## Some buttons like download, bookmark.
		TmpButton1 = gtk.Button()
		TmpButton1.set_focus_on_click(False)
		TmpButton2 = gtk.Button()
		TmpButton2.set_focus_on_click(False)
		### style setting for buttons
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_GOTO_BOTTOM, gtk.ICON_SIZE_LARGE_TOOLBAR)
		TmpButton1.add(icon)
		#TmpButton1.connect('clicked', self.DownloadAll, cid, info['Name'], imgcode, index)
		TmpButton1.connect('clicked', self.DownloadMenu, cid, info['Name'], imgcode, index)
		TmpButton1.set_tooltip_text('Download')
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_LARGE_TOOLBAR)
		TmpButton2.add(icon)
		TmpButton2.set_tooltip_text('Add to bookmark')
		TmpButton2.connect('clicked', self.NewBookmark, cid, info['Name'])
		### Packing
		TmpHBox2 = gtk.HBox()
		TmpHBox2.pack_end(TmpButton2, False, False, 2)
		TmpHBox2.pack_end(TmpButton1, False, False)
		TmpHBox2.show_all()
		## Packing
		TmpHBox1 = gtk.HBox(False, 0)
		TmpVBox2 = gtk.VBox(False, 0)
		TmpHBox1.pack_start(cover, True, True, 0)
		TmpHBox1.pack_start(TmpLabel, True, True, 0)
		TmpHBox1.show()
		TmpVBox2.pack_start(TmpHBox2, False, False, 0)
		TmpVBox2.pack_start(TmpHBox1, True, True, 0)
		TmpVBox2.show()
		TmpFrame2.add(TmpVBox2)
		
		# Packing
		TmpVBox1 = gtk.VBox(False, 0)
		TmpScrollWin = gtk.ScrolledWindow()
		TmpScrollWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		TmpScrollWin.add_with_viewport(TmpTable)
		TmpScrollWin.show()
		TmpVBox1.pack_start(TmpFrame2, True, True, 0)
		TmpVBox1.pack_start(TmpScrollWin, True, True, 0)
		TmpVBox1.show()
		# New Page
		self.NoteBook1.append_page(TmpVBox1, 
				self.NewTabLabel(info['Name'], TmpVBox1));
		self.ProgressBar.set_fraction(1)
		self.StatusBar.push(0, 'Ready')
	
	def GetWebData(self, host, path, ConvertFlag=True):
		get = httplib.HTTPConnection(host)
		get.request('GET', path, '', {'Referer': 'http://' + host + '/',
			'User-Agent': 'Mozilla/5.0  AppleWebKit/537.11 (KHTML, like Gecko)\
			Chromium/23.0.1271.97 Chrome/23.0.1271.97 Safari/537.11'})
		index = get.getresponse()
		
		# Checking http status code
		if index.status != 200:
			self.StatusBar.push(0, str(index.status) + ' ' + index.reason)
			get.close()
			return
		
		if ConvertFlag == True:
			data = index.read().decode('big5')
		else:
			data = index.read()
		get.close()
		return data

	def GetComicIndex(self, src):
		index = BeautifulSoup(src)
		ls = []

		# Remove needless string
		for i in index.find(id='rp_ctl00_tb_comic').find_all('script'):
			i.decompose()
		
		# Generate the index
		for i in index.find(id='rp_ctl00_tb_comic').table.find_all('table'):
			if i == index.find(id='rp_ctl00_tb_comic').table.table:
				continue	# Ignore the first table
			for j in i.stripped_strings:
				ls.append(j)
			
		return ls

	def GetComicInfo(self, src):
		src = BeautifulSoup(src)
		dic = {}
		
		# Get the comic name
		dic.update({'Name': 
			src.table.find_next_sibling('table').table.table.table.get_text('', True)})

		# Get the comic introduction
		dic.update({'Intro':
			src.table.find_next_sibling('table').table.find_all('td')[-1].get_text('', True)})
		
		return dic

	def CleanFrame(self, widget):
		self.frame1.remove(self.table1)
		self.frame2.remove(self.label2)
		self.ComicID.set_text('')
		self.StatusBar.push(0, 'Ready')
	
	def RemovePage(self, widget, target):
		page = self.NoteBook1.page_num(target)
		if page == -1:
			return
		self.NoteBook1.remove_page(page)

	def GetImgCode(self, cid):
		"""
		This function will generate a tow dimension list.
		"""
		src = self.GetWebData('www.8comic.com', '/view/' + cid + '.html')
		codes= BeautifulSoup(src)
		codes = str(codes.find_all('script', src='')[-1])
		start = codes.find('var codes=')
		end = codes.find('.split(\'|\')')
		codes = codes[start+11:end-1].split('|')
		
		# Simulating the decoding
		itemid = cid
		ls = []
		for i in codes:
			num = i.split(' ')[0]
			sid = i.split(' ')[1]
			did = i.split(' ')[2]
			page = i.split(' ')[3]
			code = i.split(' ')[4]
			ch = int(num) # ch for Chapter
			j = []
			for p in range(1, int(page)+1):
				m = (((p - 1) // 10) % 10) + (((p - 1) % 10) * 3)
				if p < 10:
					img = "00" + str(p)
				elif p < 100:
					img = "0" + str(p)
				else:
					img = str(p)
				img += '_' + code[m:m+3]
				url = 'img' + sid + ".8comic.com"
				path = "/" + did + "/" + itemid + "/" + num + "/" + img + ".jpg"
				j.append((url, path))
			ls.append(j)
		
		return ls
	
	def ShowAboutInfo(self, widget):
		m = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		m.set_markup("Comic Creeper")
		m.action_area.get_children()[0].connect('clicked', lambda widget: m.destroy())
		m.show()
	
	def CommitComicID(self, widget, event):
		if event.keyval == 65293:
			self.Search(widget, self.ComicID)
	
	def ShowImgPage(self, widget, UrlList, TabName):
		"""
		Create a new tab for viewing comic.
		"""
		# Scrolled Window
		TmpScrollWin = gtk.ScrolledWindow()
		TmpScrollWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		TmpScrollWin.show()
		
		# VBox
		TmpVBox1 = gtk.VBox(True, 0)
		TmpVBox1.show()
		
		# New Page
		self.NoteBook1.append_page(TmpScrollWin, 
				self.NewTabLabel(TabName, TmpScrollWin))
		
		# Packing
		TmpScrollWin.add_with_viewport(TmpVBox1)

		# Show images
		for i in UrlList:
			image = gtk.Image()
			rawimg = self.GetWebData(i[0], i[1], False)
			loader = gtk.gdk.PixbufLoader()
			loader.write(rawimg)
			loader.close()
			image.set_from_pixbuf(loader.get_pixbuf())
			image.show()
			TmpVBox1.pack_start(image, False, True, 0)
	
	def ShowImgPage_thread(self, widget, UrlList, TabName):
		"""
		Let ShowImgPage run in a thread.
		"""
		t = Thread(target=self.ShowImgPage, args=(widget, UrlList, TabName))
		t.daemon = True
		t.start()
	
	def StepProgressBar(self, progressbar, step):
		current = progressbar.get_fraction()
		if (current + step) > 1:
			progressbar.set_fraction(current + step - 1)
		else:
			progressbar.set_fraction(current + step)
	
	def ToggleTab(self, widget, tab, delete_direct=False):
		"""
		The close button on the tab label should let 'delete_direct' be true.
		"""
		num = self.NoteBook1.page_num(tab)
		if tab.get_visible() == True:
			if delete_direct == True:
				tab.hide_all()
			elif self.NoteBook1.get_current_page() != num:
				self.NoteBook1.set_current_page(num)
			else:
				tab.hide_all()
		else:
			tab.show_all()
			self.NoteBook1.set_current_page(num)

	def NewTabLabel(self, text, widget, call_back=None, *user_data):
		"""
		About the widget arg:
			The button click event will pass the widget 
			in the self.NoteBook1 to RemovePage.
			RemovePage use this arg to get the page id,
			then the tab will be delete.
		call_back:
			The default behavior of the button is call
			self.Remove.
			If it need anthor call back function, 
			just pass to this arg.
		This function will return a gtk.HBox.
		Put a label and close button in HBox.
		"""
		# Label for showing text
		label = gtk.Label(text)
		label.show()
		
		# stock icon for close button
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_SMALL_TOOLBAR)
		
		# close button
		button = gtk.Button()
		button.set_relief(gtk.RELIEF_NONE)
		button.set_focus_on_click(False)
		button.set_size_request(22, 22)
		button.add(icon)
		## handle click event
		if call_back != None:
			if user_data != None:
				button.connect('clicked', call_back, *user_data)
			else:
				button.connect('clicked', call_back)
		else:
			button.connect('clicked', self.RemovePage, widget)

		# Packing
		HBox = gtk.HBox()
		HBox.pack_start(label)
		HBox.pack_start(button, False, False)
		HBox.show_all()
		
		return HBox
	
	def NewBookmark(self, widget, comicid, name):
		"""
		First, checking if there exists same record already.
		"""
		check = self.ExecuteDB(
				'SELECT * FROM bookmark WHERE ComicID=?',
				(comicid,)).fetchone()
		if check == None:
			self.BMTreeStore.append(None, [comicid, name])
			self.ExecuteDB(''' INSERT INTO bookmark VALUES(?, ?)''',
					(comicid, name))
			self.StatusBar.push(0, name + ' added to bookmark successfully.')
		else:
			self.StatusBar.push(0, name + ' in your bookmark already!')
	
	def InitDB(self):
		"""
		if the file does not exist, 
		build the table we need.
		"""
		db_dir = self.config['FileDir'] + '/db'
		db_file = db_dir + '/local.db'
		if os.path.exists(db_dir) == False:
			os.mkdir(db_dir)
		# checking the table exist or not
		self.Sqlcon = sqlite3.connect(db_file, check_same_thread=False)
		check = {}
		for i in ('bookmark', 'history', 'config'):
			check[i] = self.ExecuteDB('SELECT * FROM SQLITE_MASTER WHERE name=?', (i,)).fetchone()
		if check['bookmark'] == None:
			self.ExecuteDB('''
					CREATE TABLE bookmark
					(
						ComicID INTEGER,
						ComicName TEXT,
						PRIMARY KEY (ComicID)
					)
					''')
		if check['history'] == None:
			self.ExecuteDB('''
					CREATE TABLE history
					(
						ComicID INTEGER,
						ComicName TEXT,
						Time TEXT
					)
					''')
		if check['config'] == None:
			self.ExecuteDB('''
					CREATE TABLE config
					(
						Key TEXT,
						Val TEXT
					)
					''')
	
	def ExecuteDB(self, command, args=None):
		"""
		args must be a list.
		"""
		cursor = self.Sqlcon.cursor()
		if args == None:
			data = cursor.execute(command)
		else:
			data = cursor.execute(command, args)
		self.Sqlcon.commit()
		return data
	
	def TreeViewClickRow(self, widget, iter, path):
		model, tmpiter = widget.get_selection().get_selected()
		comicid = model.get_value(tmpiter, 0)
		Thread(target=self.ShowIndex, args=(comicid,)).start()
	
	def BMTreeViewDel(self, widget):
		model, tmpiter = self.BMTreeView.get_selection().get_selected()
		if tmpiter != None:
			comicid = model.get_value(tmpiter, 0)
			self.ExecuteDB('DELETE FROM bookmark WHERE ComicID=?',
					(comicid,))
			model.remove(tmpiter)
	
	def HMTreeViewDel(self, widget):
		model, tmpiter = self.HMTreeView.get_selection().get_selected()
		if tmpiter != None:
			timestr = model.get_value(tmpiter, 2).decode('utf8')
			self.ExecuteDB('DELETE FROM history WHERE Time=?',
					(timestr,))
			model.remove(tmpiter)
	
	def HMTreeViewDelAll(self, widget):
		self.HMTreeStore.clear()
		self.ExecuteDB('DELETE FROM history')
	
	def DownloadSelect(self, widget, cid, cname, imgcode, index, index_store):
		"""
		This is a call back function for download button
		in the index page.
			- If the download_dir do not exist,
			it will try to create it.
			- Add a new download record to download manager
			- Write record to db.
			- Let download progress run in threads.
		"""
		download_dir = self.config['DownloadDir']
		timestr = datetime.datetime.now().strftime('%Y-%m-%d %p %H:%M')
		
		# check dir
		if os.path.exists(download_dir) == False:
			os.mkdir(download_dir)
		
		# Added a new record
		piter = self.DMTreeStore.append(None, (cid, cname, timestr, 0.0))
		self.StatusBar.push(0, 'Start to download: ' + cname)
		citer = {}
		for i in index_store:
			if i[0]:
				k = index.index(i[1])
				citer[k] = self.DMTreeStore.append(piter, (cid, i[1], None, 0.0))
		# Tread
		def down_task():
			# check comic dir
			comic_dir = download_dir + '/' + cname
			if os.path.exists(comic_dir) == False:
				os.mkdir(comic_dir)
			# get totle img count
			imgcount = 0.0
			for i in index_store:
				if i[0]:
					k = index.index(i[1])
					for j in imgcode[k]:
						imgcount += 1
			step = 100 / imgcount
			
			for i in index_store:
				if i[0]:
					# create index dir in comic_dir
					index_dir = comic_dir + '/' + i[1]
					if os.path.exists(index_dir) == False:
						os.mkdir(index_dir)
					k = index.index(i[1])
					# get img count of index
					index_count = 0.0
					for j in imgcode[k]:
						index_count += 1
					index_step = 100 / index_count
					# fetch img
					for j in imgcode[k]:
						img_name = j[1].split('/')[-1].split('_')[0] + '.jpg'
						img_file = open(index_dir + '/' + img_name, 'wb')
						img_file.write( self.GetWebData(j[0], j[1], False) )
						img_file.close()
						current = self.DMTreeStore.get_value(piter, 3)
						self.DMTreeStore.set_value(piter, 3, current + step)
						current = self.DMTreeStore.get_value(citer[k], 3)
						self.DMTreeStore.set_value(citer[k], 3, current + index_step)
					self.DMTreeStore.set_value(citer[k], 3, 100)
			self.DMTreeStore.set_value(piter, 3, 100)
			self.StatusBar.push(0, 'Finished download: ' + cname)
		
		t = Thread(target=down_task)
		t.daemon = True
		t.start()
	
	def DownloadMenu(self, widget, cid, cname, imgcode, index):
		# function
		def check_toggled(cell, row):
			index_store[row][0] = not index_store[row][0]
		# download dialog
		dialog = gtk.Dialog('Download Menu',
						None,
						gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
						(gtk.STOCK_OK, gtk.RESPONSE_OK,
						gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		dialog.set_size_request(640, 480)
		# download dir selection
		label1 = gtk.Label('Download Directory: ')
		entry1 = gtk.Entry()
		entry1.set_text(self.config['DownloadDir'])
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
		button1 = gtk.Button()
		button1.add(icon)
		button1.connect('clicked', self.SelectDownloadDir, entry1)
		# tree view for selection
		index_store = gtk.TreeStore(bool, str)
		index_col1 = gtk.TreeViewColumn('#')
		index_col2 = gtk.TreeViewColumn('Name')
		index_col1.set_resizable(True)
		index_col2.set_resizable(True)
		index_cell1 = gtk.CellRendererToggle()
		index_cell1.set_activatable(True)
		index_cell1.connect('toggled', check_toggled)
		index_cell2 = gtk.CellRendererText()
		index_col1.pack_start(index_cell1, True)
		index_col2.pack_start(index_cell2, True)
		index_col1.add_attribute(index_cell1, 'active', 0)
		index_col2.add_attribute(index_cell2, 'text', 1)
		index_tree = gtk.TreeView(index_store)
		index_selection = index_tree.get_selection()
		index_selection.set_mode(gtk.SELECTION_MULTIPLE)
		index_selection.selected_foreach(check_toggled)
		index_tree.append_column(index_col1)
		index_tree.append_column(index_col2)
		index_scroll = gtk.ScrolledWindow()
		index_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		index_scroll.set_vadjustment(index_tree.get_vadjustment())
		index_scroll.add(index_tree)
		## Add index row
		for i in index:
			index_store.append(None, (False, i))
		# some tool button
		def sel_all_toggled(widget):
			if widget.get_active():
				for i in index_store:
					i[0] = True
			else:
				for i in index_store:
					i[0] = False
		
		select_all = gtk.CheckButton('Select all')
		select_all.connect('toggled', sel_all_toggled)
		# Packing
		HBox1 = gtk.HBox()
		HBox1.pack_start(label1, False, False, 2)
		HBox1.pack_start(entry1, True, True)
		HBox1.pack_start(button1, False, False, 2)
		HBox2 = gtk.HBox()
		HBox2.pack_start(select_all, False, False, 2)
		dialog.vbox.pack_start(HBox1, False, True)
		dialog.vbox.pack_start(HBox2, False, True)
		dialog.vbox.pack_start(index_scroll, True, True)
		dialog.vbox.show_all()
		
		res = dialog.run()
		if res == gtk.RESPONSE_OK:
			self.DownloadSelect(widget, cid, cname, imgcode, index, index_store)
		dialog.destroy()
	
	def LogHistory(self, comicid, cname):
		timestr = datetime.datetime.now().strftime('%Y-%m-%d %p %H:%M').decode('utf8')
		self.HMTreeStore.append(None, [comicid, cname, timestr])
		self.ExecuteDB('INSERT INTO history VALUES(?, ?, ?)',
				(comicid, cname, timestr))
	
	def SaveConfig(self, widget, key, val_entry):
		val = val_entry.get_text()
		# setting db
		check = self.ExecuteDB('SELECT * FROM config WHERE key=?', (key,)).fetchone()
		if check != None:
			self.ExecuteDB('UPDATE config SET val=? WHERE key=?', (val, key))
		else:
			self.ExecuteDB('INSERT INTO config VALUES (?, ?)', (key, val))
		# setting dictionary
		self.config[key] = val
		self.StatusBar.push(0, 'Configuration saved!')
	
	def SelectDownloadDir(self, widget, val_entry):
		val = val_entry.get_text()
		dialog = gtk.FileChooserDialog('Choose a directory',
						None,
						gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
							gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_current_folder(val)
		res = dialog.run()
		if res == gtk.RESPONSE_OK:
			val_entry.set_text(dialog.get_filename())
		dialog.destroy()
	
if __name__ == '__main__':
	cc = creeper()
	cc.main()
